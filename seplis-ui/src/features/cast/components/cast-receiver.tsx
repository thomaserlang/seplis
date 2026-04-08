import { getPlayRequestSources } from '@/features/play/api/play-request-sources.api'
import { getPlayServerMedia } from '@/features/play/api/play-server-media.api'
import { MAX_BITRATE } from '@/features/play/constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
} from '@/features/play/types/play-source.types'
import React, { useEffect, useRef, useState } from 'react'
import { CAST_NAMESPACE, CastLoadData, CastSenderMessage } from '../types/cast-messages.types'

const LOG_TAG = 'SEPLIS'

// CAF context is a singleton — guard against React StrictMode double-invoke
let receiverInitialized = false

interface ReceiverState {
    loadData: CastLoadData
    playRequestSources: PlayRequestSources[]
    playRequestSource: PlayRequestSource
    subtitleTracks: CafTrack[]
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
    const [status, setStatus] = useState('Waiting for connection…')
    const stateRef = useRef<ReceiverState | null>(null)
    const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const logRef = useRef<(msg: string, ...args: unknown[]) => void>(() => {})

    useEffect(() => {
        if (receiverInitialized) return
        receiverInitialized = true

        const cast = (window as any).cast
        if (!cast?.framework) {
            const msg = 'Cast Receiver SDK not found. Check cast-receiver.html script tags.'
            console.error('[SEPLIS]', msg)
            setStatus(`Error: ${msg}`)
            return
        }

        // ── Debug logger ──────────────────────────────────────────────────
        // https://developers.google.com/cast/docs/debugging/cast_debug_logger
        const debugLogger = (cast as any).debug?.CastDebugLogger?.getInstance()
        if (debugLogger) {
            debugLogger.setEnabled(true)
            debugLogger.showDebugLogs(true)
            // Show all framework core events and media status in the overlay
            debugLogger.loggerLevelByEvents = {
                'cast.framework.events.category.CORE':
                    cast.framework.LoggerLevel.INFO,
                'cast.framework.events.EventType.MEDIA_STATUS':
                    cast.framework.LoggerLevel.DEBUG,
            }
        } else {
            console.warn('[SEPLIS] CastDebugLogger not available — add caf_debugger.js to cast-receiver.html')
        }

        // Unified log helper: writes to console + debug overlay
        const log = (msg: string, ...args: unknown[]) => {
            console.log(`[${LOG_TAG}]`, msg, ...args)
            debugLogger?.info(LOG_TAG, msg, ...args)
        }
        logRef.current = log

        log('SDK ready, initialising receiver context')

        const context = cast.framework.CastReceiverContext.getInstance()
        const playerManager = context.getPlayerManager()

        // ── System events ─────────────────────────────────────────────────
        context.addEventListener(cast.framework.system.EventType.READY, () => {
            log('Receiver READY')
            setStatus('Ready — waiting for content…')
        })
        context.addEventListener(cast.framework.system.EventType.ERROR, (e: any) => {
            log('System ERROR', e)
            setStatus(`System error: ${JSON.stringify(e)}`)
        })
        context.addEventListener(cast.framework.system.EventType.SENDER_CONNECTED, (e: any) => {
            log('Sender connected', e?.senderId)
            setStatus('Sender connected')
        })
        context.addEventListener(cast.framework.system.EventType.SENDER_DISCONNECTED, (e: any) => {
            log('Sender disconnected', e?.senderId)
        })

        // ── Player events ─────────────────────────────────────────────────
        playerManager.addEventListener(
            cast.framework.events.EventType.ERROR,
            (e: any) => log('Player ERROR', e),
        )
        playerManager.addEventListener(
            cast.framework.events.EventType.BUFFERING,
            (e: any) => log('Buffering', e?.isBuffering),
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

                // Short-circuit: URL already resolved by a receiver-side reload
                if (customData.isReload) {
                    log('isReload=true, passing through')
                    return loadRequest
                }

                setStatus('Loading sources…')
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

                    setStatus('Negotiating stream…')
                    // Codec detection runs on the Chromecast's Chromium browser
                    const mediaData = await getPlayServerMedia({
                        playRequestSource,
                        audio: customData.audio,
                        maxBitrate:
                            customData.maxBitrate < MAX_BITRATE
                                ? customData.maxBitrate
                                : undefined,
                        startTime: customData.startTime,
                    })
                    log('Media URL ready', { canDirectPlay: mediaData.can_direct_play, url: mediaData.hls_url })

                    if (keepAliveRef.current) clearInterval(keepAliveRef.current)
                    keepAliveRef.current = setInterval(() => {
                        fetch(mediaData.keep_alive_url).catch(() => {})
                    }, 5000)

                    const subtitleTracks = buildSubtitleTracks(playRequestSource)
                    stateRef.current = {
                        loadData: customData,
                        playRequestSources: sources,
                        playRequestSource,
                        subtitleTracks,
                    }

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
                    loadRequest.media.duration = playRequestSource.source.duration
                    loadRequest.media.tracks = subtitleTracks
                    loadRequest.media.metadata = {
                        metadataType: 0,
                        title: customData.title,
                        subtitle: customData.secondaryTitle,
                    }
                    loadRequest.currentTime = customData.startTime ?? 0

                    setStatus('Playing')
                    return loadRequest
                } catch (e) {
                    const msg = e instanceof Error ? e.message : String(e)
                    log('LOAD ERROR', msg)
                    setStatus(`Load error: ${msg}`)
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
                        subtitleTracks,
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

    const isPlaying = status === 'Playing'

    return (
        <div
            style={{
                position: 'relative',
                width: '100vw',
                height: '100vh',
                background: '#111',
                fontFamily: 'sans-serif',
                overflow: 'hidden',
            }}
        >
            {/* CAF player — always rendered so CAF can control it */}
            {React.createElement('cast-media-player', {
                style: {
                    position: 'absolute',
                    inset: 0,
                    width: '100%',
                    height: '100%',
                    zIndex: 0,
                },
            })}

            {/* Splash — sits above the player while no content is playing */}
            {!isPlaying && (
                <div
                    style={{
                        position: 'absolute',
                        inset: 0,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        gap: '1rem',
                        zIndex: 1,
                        background: '#111',
                    }}
                >
                    <div
                        style={{
                            fontSize: '4rem',
                            fontWeight: 700,
                            letterSpacing: '0.25em',
                            opacity: 0.9,
                        }}
                    >
                        SEPLIS
                    </div>
                    <div
                        style={{
                            fontSize: '1.1rem',
                            opacity: 0.5,
                            maxWidth: '60%',
                            textAlign: 'center',
                        }}
                    >
                        {status}
                    </div>
                </div>
            )}
        </div>
    )
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
