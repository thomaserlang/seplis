import { getPlayRequestSources } from '@/features/play/api/play-request-sources.api'
import { getPlayServerMedia } from '@/features/play/api/play-server-media.api'
import { MAX_BITRATE } from '@/features/play/constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
} from '@/features/play/types/play-source.types'
import { useEffect, useRef } from 'react'
import { CAST_NAMESPACE, CastLoadData, CastSenderMessage } from '../types/cast-messages.types'

const LOG_TAG = 'SEPLIS'

// CAF context is a singleton — guard against React StrictMode double-invoke
let receiverInitialized = false

interface ReceiverState {
    loadData: CastLoadData
    playRequestSources: PlayRequestSources[]
    playRequestSource: PlayRequestSource
}

interface CafTrack {
    trackId: number
    type: string
    subtype: string
    name: string
    language: string
    trackContentId: string
    trackContentType: string
}

export function CastReceiver() {
    const stateRef = useRef<ReceiverState | null>(null)
    const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null)

    useEffect(() => {
        if (receiverInitialized) return
        receiverInitialized = true

        const cast = (window as any).cast
        if (!cast?.framework) {
            console.error('[SEPLIS] Cast Receiver SDK not found — check cast-receiver.html script tags.')
            return
        }

        const debugLogger = (cast as any).debug?.CastDebugLogger?.getInstance()
        if (debugLogger) {
            debugLogger.loggerLevelByEvents = {
                'cast.framework.events.category.CORE': cast.framework.LoggerLevel.INFO,
                'cast.framework.events.EventType.MEDIA_STATUS': cast.framework.LoggerLevel.DEBUG,
            }
            debugLogger.loggerLevelByTags = {
                [LOG_TAG]: cast.framework.LoggerLevel.DEBUG,
            }
        }

        const log = (msg: string, ...args: unknown[]) => {
            console.log(`[${LOG_TAG}]`, msg, ...args)
            debugLogger?.info(LOG_TAG, msg, ...args)
        }

        log('SDK ready, initialising receiver context')

        const context = cast.framework.CastReceiverContext.getInstance()
        const playerManager = context.getPlayerManager()

        context.addEventListener(cast.framework.system.EventType.READY, () => {
            if (import.meta.env.DEV && debugLogger && !debugLogger.debugOverlayElement_) {
                debugLogger.setEnabled(true)
                debugLogger.showDebugLogs(true)
            }
            log('Receiver READY')
        })

        playerManager.addEventListener(
            cast.framework.events.EventType.ERROR,
            (e: any) => log('Player ERROR', e),
        )

        // ── LOAD interceptor ──────────────────────────────────────────────
        playerManager.setMessageInterceptor(
            cast.framework.messages.MessageType.LOAD,
            async (loadRequest: any) => {
                const customData = loadRequest.media?.customData as
                    | (CastLoadData & { isReload?: boolean })
                    | undefined

                log('LOAD interceptor', { isReload: customData?.isReload, hasPlayRequests: !!customData?.playRequests })

                if (!customData?.playRequests) return loadRequest

                if (customData.isReload) {
                    log('isReload=true, passing through')
                    return loadRequest
                }

                try {
                    const sources = await getPlayRequestSources({
                        playRequests: customData.playRequests,
                    })
                    log('Sources fetched', sources?.length)

                    if (!sources?.length) throw new Error('No play sources available')

                    const playRequestSource = resolveSource(
                        sources,
                        customData.sourcePlayId,
                        customData.sourceIndex,
                    )
                    log('Source resolved', playRequestSource.source.resolution, playRequestSource.source.codec)

                    const mediaData = await getPlayServerMedia({
                        playRequestSource,
                        audio: customData.audio,
                        maxBitrate:
                            customData.maxBitrate < MAX_BITRATE
                                ? customData.maxBitrate
                                : undefined,
                        startTime: customData.startTime,
                    })
                    log('Media URL ready', { canDirectPlay: mediaData.can_direct_play })

                    if (keepAliveRef.current) clearInterval(keepAliveRef.current)
                    keepAliveRef.current = setInterval(() => {
                        fetch(mediaData.keep_alive_url).catch(() => {})
                    }, 5000)

                    stateRef.current = {
                        loadData: customData,
                        playRequestSources: sources,
                        playRequestSource,
                    }

                    const subtitleTracks = buildSubtitleTracks(playRequestSource)
                    if (customData.subtitle) {
                        const trackId = findSubtitleTrackId(playRequestSource, customData.subtitle)
                        if (trackId !== null) loadRequest.activeTrackIds = [trackId]
                    }

                    const url = mediaData.can_direct_play
                        ? mediaData.direct_play_url
                        : mediaData.hls_url

                    loadRequest.media.contentId = url
                    loadRequest.media.contentType = mediaData.can_direct_play
                        ? 'video/mp4'
                        : 'application/x-mpegURL'
                    loadRequest.media.streamType = cast.framework.messages.StreamType.BUFFERED
                    loadRequest.media.duration = playRequestSource.source.duration
                    loadRequest.media.tracks = subtitleTracks
                    loadRequest.media.metadata = {
                        metadataType: 0, // GENERIC
                        title: customData.title,
                        subtitle: customData.secondaryTitle,
                    }
                    loadRequest.currentTime = customData.startTime ?? 0

                    return loadRequest
                } catch (e) {
                    const msg = e instanceof Error ? e.message : String(e)
                    log('LOAD ERROR', msg)
                    throw e
                }
            },
        )

        // ── Custom messages (settings changes from sender) ────────────────
        context.addCustomMessageListener(
            CAST_NAMESPACE,
            async (event: { data: CastSenderMessage; senderId: string }) => {
                const msg = event.data
                const current = stateRef.current
                log('Custom message', msg.type)
                if (!current) return

                if (msg.type === 'setSubtitle') {
                    const ttm = playerManager.getTextTracksManager()
                    if (!msg.subtitle) {
                        ttm.setActiveByIds([])
                    } else {
                        const trackId = findSubtitleTrackId(current.playRequestSource, msg.subtitle)
                        if (trackId !== null) ttm.setActiveByIds([trackId])
                    }
                    stateRef.current = {
                        ...current,
                        loadData: { ...current.loadData, subtitle: msg.subtitle },
                    }
                    return
                }

                let newLoadData = { ...current.loadData }
                let newPlayRequestSource = current.playRequestSource

                if (msg.type === 'setAudio') {
                    newLoadData.audio = msg.audio
                } else if (msg.type === 'setBitrate') {
                    newLoadData.maxBitrate = msg.maxBitrate
                } else if (msg.type === 'setSource') {
                    const reqSources = current.playRequestSources.find(
                        (s) => s.request.play_id === msg.playId,
                    )
                    if (reqSources) {
                        const src = reqSources.sources.find((s) => s.index === msg.sourceIndex)
                        if (src) {
                            newPlayRequestSource = { request: reqSources.request, source: src }
                            newLoadData.sourcePlayId = msg.playId
                            newLoadData.sourceIndex = msg.sourceIndex
                        }
                    }
                }

                try {
                    const currentTime = playerManager.getCurrentTimeSec() ?? 0
                    const mediaData = await getPlayServerMedia({
                        playRequestSource: newPlayRequestSource,
                        audio: newLoadData.audio,
                        maxBitrate:
                            newLoadData.maxBitrate < MAX_BITRATE
                                ? newLoadData.maxBitrate
                                : undefined,
                        startTime: currentTime,
                    })

                    if (keepAliveRef.current) clearInterval(keepAliveRef.current)
                    keepAliveRef.current = setInterval(() => {
                        fetch(mediaData.keep_alive_url).catch(() => {})
                    }, 5000)

                    const url = mediaData.can_direct_play
                        ? mediaData.direct_play_url
                        : mediaData.hls_url
                    const subtitleTracks = buildSubtitleTracks(newPlayRequestSource)

                    stateRef.current = {
                        loadData: newLoadData,
                        playRequestSources: current.playRequestSources,
                        playRequestSource: newPlayRequestSource,
                    }

                    playerManager.load({
                        type: 'LOAD',
                        media: {
                            contentId: url,
                            contentType: mediaData.can_direct_play
                                ? 'video/mp4'
                                : 'application/x-mpegURL',
                            customData: { ...newLoadData, isReload: true },
                            tracks: subtitleTracks,
                        },
                        currentTime,
                    })
                } catch (e) {
                    log('Settings reload ERROR', e instanceof Error ? e.message : String(e))
                }
            },
        )

        log('Calling context.start()')
        context.start()

        return () => {
            if (keepAliveRef.current) clearInterval(keepAliveRef.current)
        }
    }, [])

    return null
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function resolveSource(
    sources: PlayRequestSources[],
    sourcePlayId: string,
    sourceIndex: number,
): PlayRequestSource {
    const reqSources =
        sources.find((s) => s.request.play_id === sourcePlayId) ?? sources[0]
    const source =
        reqSources.sources.find((s: PlaySource) => s.index === sourceIndex) ??
        reqSources.sources[0]
    return { request: reqSources.request, source }
}

function buildSubtitleTracks(prs: PlayRequestSource): CafTrack[] {
    return prs.source.subtitles.map((sub, i) => ({
        trackId: i + 1,
        type: 'TEXT',
        subtype: 'SUBTITLES',
        name: sub.title || sub.language,
        language: sub.language,
        trackContentId:
            `${prs.request.play_url}/subtitle-file` +
            `?play_id=${prs.request.play_id}` +
            `&source_index=${prs.source.index}` +
            `&offset=0` +
            `&lang=${sub.language}:${sub.index}`,
        trackContentType: 'text/vtt',
    }))
}

function findSubtitleTrackId(prs: PlayRequestSource, subtitleKey: string): number | null {
    const [lang, idxStr] = subtitleKey.split(':')
    const idx = prs.source.subtitles.findIndex(
        (s) => s.language === lang && s.index === parseInt(idxStr),
    )
    return idx === -1 ? null : idx + 1
}
