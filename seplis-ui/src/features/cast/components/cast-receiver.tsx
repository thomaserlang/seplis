import { getPlayRequestSources } from '@/features/play/api/play-request-sources.api'
import { getPlayServerMedia } from '@/features/play/api/play-server-media.api'
import { MAX_BITRATE } from '@/features/play/constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
} from '@/features/play/types/play-source.types'
import { useEffect, useRef } from 'react'
import React from 'react'
import { CAST_NAMESPACE, CastLoadData, CastSenderMessage } from '../types/cast-messages.types'

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
    contentId: string
    contentType: string
}

export function CastReceiver() {
    const stateRef = useRef<ReceiverState | null>(null)
    const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null)

    useEffect(() => {
        const cast = (window as any).cast
        if (!cast?.framework) {
            console.error(
                '[Cast Receiver] SDK not found — check that the receiver script ' +
                'is loaded before React in index.html.',
            )
            return
        }

        const context = cast.framework.CastReceiverContext.getInstance()
        const playerManager = context.getPlayerManager()

        // ── LOAD interceptor ───────────────────────────────────────────────
        // This runs whenever the sender calls loadMedia(), AND whenever we
        // call playerManager.load() from the receiver for settings changes.
        // The `isReload` flag in customData lets us short-circuit the
        // expensive API fetch on receiver-triggered reloads.
        playerManager.setMessageInterceptor(
            cast.framework.messages.MessageType.LOAD,
            async (loadRequest: any) => {
                const customData = loadRequest.media?.customData as
                    | (CastLoadData & { isReload?: boolean })
                    | undefined

                if (!customData?.playRequests) return loadRequest

                // Short-circuit: URL already resolved, just play it
                if (customData.isReload) return loadRequest

                try {
                    const sources = await getPlayRequestSources({
                        playRequests: customData.playRequests,
                    })

                    if (!sources?.length) throw new Error('No play sources available')

                    const playRequestSource = resolveSource(
                        sources,
                        customData.sourcePlayId,
                        customData.sourceIndex,
                    )

                    // getPlayServerMedia runs on the Chromecast's Chromium browser,
                    // so getSupportedVideoCodecs() / canPlayType() reflect what
                    // the Chromecast device actually supports.
                    const mediaData = await getPlayServerMedia({
                        playRequestSource,
                        audio: customData.audio,
                        maxBitrate:
                            customData.maxBitrate < MAX_BITRATE
                                ? customData.maxBitrate
                                : undefined,
                        startTime: customData.startTime,
                    })

                    // Restart keep-alive for this session
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

                    // Activate the requested subtitle track
                    if (customData.subtitle) {
                        const trackId = findSubtitleTrackId(
                            playRequestSource,
                            customData.subtitle,
                        )
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
                        metadataType: 0, // GenericMediaMetadata
                        title: customData.title,
                        subtitle: customData.secondaryTitle,
                    }
                    loadRequest.currentTime = customData.startTime ?? 0

                    return loadRequest
                } catch (e) {
                    console.error('[Cast Receiver] Failed to load media', e)
                    throw e
                }
            },
        )

        // ── Custom message listener (settings changes from sender) ─────────
        context.addCustomMessageListener(
            CAST_NAMESPACE,
            async (event: { data: CastSenderMessage; senderId: string }) => {
                const msg = event.data
                const current = stateRef.current
                if (!current) return

                // Subtitle toggle — no reload needed, just switch tracks
                if (msg.type === 'setSubtitle') {
                    const ttm = playerManager.getTextTracksManager()
                    if (!msg.subtitle) {
                        ttm.setActiveByIds([])
                    } else {
                        const trackId = findSubtitleTrackId(
                            current.playRequestSource,
                            msg.subtitle,
                        )
                        if (trackId !== null) ttm.setActiveByIds([trackId])
                    }
                    stateRef.current = {
                        ...current,
                        loadData: { ...current.loadData, subtitle: msg.subtitle },
                    }
                    return
                }

                // Audio / bitrate / source changes need a new media URL
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
                        const src = reqSources.sources.find(
                            (s) => s.index === msg.sourceIndex,
                        )
                        if (src) {
                            newPlayRequestSource = {
                                request: reqSources.request,
                                source: src,
                            }
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

                    // Restart keep-alive for the new session URL
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

                    // Reload via playerManager. isReload=true bypasses the full
                    // API fetch in the interceptor — the URL is already resolved.
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
                    console.error('[Cast Receiver] Failed to reload after settings change', e)
                }
            },
        )

        // start() must be called LAST, after all interceptors/listeners are set
        context.start()

        return () => {
            if (keepAliveRef.current) clearInterval(keepAliveRef.current)
        }
    }, [])

    // <cast-media-player> is the CAF web component that handles HLS playback,
    // subtitles, and the standard Cast receiver UI automatically.
    // React.createElement is used directly because TypeScript doesn't know
    // about this custom element in the JSX IntrinsicElements map.
    return (
        <div style={{ width: '100vw', height: '100vh', background: '#000' }}>
            {React.createElement('cast-media-player', {
                style: { width: '100%', height: '100%' },
            })}
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
        contentId:
            `${prs.request.play_url}/subtitle-file` +
            `?play_id=${prs.request.play_id}` +
            `&source_index=${prs.source.index}` +
            `&offset=0` +
            `&lang=${sub.language}:${sub.index}`,
        contentType: 'text/vtt',
    }))
}

/** Returns the 1-based trackId for a subtitle key like "eng:0", or null. */
function findSubtitleTrackId(prs: PlayRequestSource, subtitleKey: string): number | null {
    const [lang, idxStr] = subtitleKey.split(':')
    const idx = prs.source.subtitles.findIndex(
        (s) => s.language === lang && s.index === parseInt(idxStr),
    )
    return idx === -1 ? null : idx + 1
}
