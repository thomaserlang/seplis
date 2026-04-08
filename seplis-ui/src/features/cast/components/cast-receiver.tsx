import { getPlayRequestSources } from '@/features/play/api/play-request-sources.api'
import { getPlayServerMedia } from '@/features/play/api/play-server-media.api'
import { MAX_BITRATE } from '@/features/play/constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
} from '@/features/play/types/play-source.types'
import { useEffect, useRef, useState } from 'react'
import { CastLoadData, CAST_NAMESPACE, CastSenderMessage } from '../types/cast-messages.types'

interface ReceiverPlayState {
    loadData: CastLoadData
    playRequestSources: PlayRequestSources[]
    playRequestSource: PlayRequestSource
}

export function CastReceiver() {
    const videoRef = useRef<HTMLVideoElement>(null)
    const [playState, setPlayState] = useState<ReceiverPlayState | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const playStateRef = useRef<ReceiverPlayState | null>(null)
    const keepAliveRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const keepAliveUrlRef = useRef<string | null>(null)

    useEffect(() => {
        const script = document.createElement('script')
        script.src =
            'https://www.gstatic.com/cast/sdk/libs/caf_receiver/v3/cast_receiver_framework.js'
        script.onload = initReceiver
        script.onerror = () => setError('Failed to load Cast SDK')
        document.head.appendChild(script)
        return () => {
            document.head.removeChild(script)
        }
    }, [])

    const initReceiver = () => {
        const cast = (window as any).cast
        const context = cast.framework.CastReceiverContext.getInstance()
        const playerManager = context.getPlayerManager()

        // Give CAF control over our video element
        if (videoRef.current) {
            playerManager.setMediaElement(videoRef.current)
        }

        // Intercept LOAD to resolve the actual HLS/MP4 URL from the play server
        playerManager.setMessageInterceptor(
            cast.framework.messages.MessageType.LOAD,
            async (loadRequest: any) => {
                const customData = loadRequest.media.customData as CastLoadData
                if (!customData?.playRequests) return loadRequest

                setIsLoading(true)
                setError(null)

                try {
                    const sources = await getPlayRequestSources({ playRequests: customData.playRequests })

                    if (!sources || sources.length === 0) {
                        throw new Error('No play sources available')
                    }

                    const playRequestSource = resolveSource(
                        sources,
                        customData.sourcePlayId,
                        customData.sourceIndex,
                    )

                    // getPlayServerMedia runs on the Chromecast's browser,
                    // so codec detection reflects what Chromecast actually supports
                    const mediaData = await getPlayServerMedia({
                        playRequestSource,
                        audio: customData.audio,
                        maxBitrate:
                            customData.maxBitrate < MAX_BITRATE
                                ? customData.maxBitrate
                                : undefined,
                        startTime: customData.startTime,
                    })

                    // Start keep-alive for the play session
                    if (keepAliveRef.current) clearInterval(keepAliveRef.current)
                    keepAliveUrlRef.current = mediaData.keep_alive_url
                    keepAliveRef.current = setInterval(() => {
                        if (keepAliveUrlRef.current) {
                            fetch(keepAliveUrlRef.current).catch(() => {})
                        }
                    }, 5000)

                    // Build subtitle tracks for CAF
                    const subtitleTracks = playRequestSource.source.subtitles.map(
                        (sub, i) => ({
                            trackId: i + 1,
                            type: 'TEXT',
                            subtype: 'SUBTITLES',
                            name: sub.title || sub.language,
                            language: sub.language,
                            contentId:
                                `${playRequestSource.request.play_url}/subtitle-file` +
                                `?play_id=${playRequestSource.request.play_id}` +
                                `&source_index=${playRequestSource.source.index}` +
                                `&offset=0` +
                                `&lang=${sub.language}:${sub.index}`,
                            contentType: 'text/vtt',
                        }),
                    )

                    // Activate selected subtitle track
                    if (customData.subtitle) {
                        const [lang, idxStr] = customData.subtitle.split(':')
                        const subIdx = playRequestSource.source.subtitles.findIndex(
                            (s) => s.language === lang && s.index === parseInt(idxStr),
                        )
                        if (subIdx !== -1) {
                            loadRequest.activeTrackIds = [subIdx + 1]
                        }
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

                    const newState: ReceiverPlayState = {
                        loadData: customData,
                        playRequestSources: sources,
                        playRequestSource,
                    }
                    playStateRef.current = newState
                    setPlayState(newState)
                    setIsLoading(false)

                    return loadRequest
                } catch (e) {
                    const msg = e instanceof Error ? e.message : 'Failed to load media'
                    setError(msg)
                    setIsLoading(false)
                    throw e
                }
            },
        )

        // Handle settings changes from the sender
        context.addCustomMessageListener(
            CAST_NAMESPACE,
            async (event: { data: CastSenderMessage; senderId: string }) => {
                const msg = event.data
                const current = playStateRef.current
                if (!current) return

                if (msg.type === 'setSubtitle') {
                    if (!msg.subtitle) {
                        playerManager.setActiveTrackIds([])
                    } else {
                        const [lang, idxStr] = msg.subtitle.split(':')
                        const subIdx = current.playRequestSource.source.subtitles.findIndex(
                            (s) => s.language === lang && s.index === parseInt(idxStr),
                        )
                        if (subIdx !== -1) {
                            playerManager.setActiveTrackIds([subIdx + 1])
                        }
                    }
                    updateState({ loadData: { ...current.loadData, subtitle: msg.subtitle } })
                    return
                }

                // Audio, bitrate, or source changes require fetching a new stream URL
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
                            newPlayRequestSource = { request: reqSources.request, source: src }
                            newLoadData.sourcePlayId = msg.playId
                            newLoadData.sourceIndex = msg.sourceIndex
                        }
                    }
                }

                try {
                    const currentTime = videoRef.current?.currentTime ?? 0
                    const mediaData = await getPlayServerMedia({
                        playRequestSource: newPlayRequestSource,
                        audio: newLoadData.audio,
                        maxBitrate:
                            newLoadData.maxBitrate < MAX_BITRATE
                                ? newLoadData.maxBitrate
                                : undefined,
                        startTime: currentTime,
                    })

                    keepAliveUrlRef.current = mediaData.keep_alive_url

                    const url = mediaData.can_direct_play
                        ? mediaData.direct_play_url
                        : mediaData.hls_url

                    // Directly update the video element src; CAF will pick up the events
                    if (videoRef.current) {
                        const v = videoRef.current
                        const wasPaused = v.paused
                        v.src = url
                        v.load()
                        v.currentTime = currentTime
                        if (!wasPaused) v.play().catch(() => {})
                    }

                    const newState: ReceiverPlayState = {
                        loadData: newLoadData,
                        playRequestSources: current.playRequestSources,
                        playRequestSource: newPlayRequestSource,
                    }
                    playStateRef.current = newState
                    setPlayState(newState)
                } catch (e) {
                    console.error('Failed to reload media after settings change', e)
                }
            },
        )

        context.start()
    }

    const updateState = (partial: Partial<ReceiverPlayState>) => {
        setPlayState((prev) => {
            if (!prev) return prev
            const next = { ...prev, ...partial }
            playStateRef.current = next
            return next
        })
    }

    return (
        <div
            style={{
                width: '100vw',
                height: '100vh',
                background: '#000',
                position: 'relative',
                overflow: 'hidden',
                fontFamily: 'sans-serif',
            }}
        >
            <video
                ref={videoRef}
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />

            {/* Metadata overlay */}
            {playState && (
                <div
                    style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: '3rem 3rem 2rem',
                        background:
                            'linear-gradient(transparent, rgba(0,0,0,0.85))',
                        color: '#fff',
                        pointerEvents: 'none',
                    }}
                >
                    {playState.loadData.title && (
                        <div
                            style={{
                                fontSize: '2rem',
                                fontWeight: 700,
                                lineHeight: 1.2,
                                textShadow: '0 1px 4px rgba(0,0,0,0.8)',
                            }}
                        >
                            {playState.loadData.title}
                        </div>
                    )}
                    {playState.loadData.secondaryTitle && (
                        <div
                            style={{
                                fontSize: '1.25rem',
                                marginTop: '0.25rem',
                                opacity: 0.8,
                                textShadow: '0 1px 4px rgba(0,0,0,0.8)',
                            }}
                        >
                            {playState.loadData.secondaryTitle}
                        </div>
                    )}
                </div>
            )}

            {/* Loading / error overlay */}
            {(isLoading || error) && (
                <div
                    style={{
                        position: 'absolute',
                        inset: 0,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: 'rgba(0,0,0,0.6)',
                        color: '#fff',
                        fontSize: '1.25rem',
                    }}
                >
                    {error ? (
                        <span style={{ color: '#f88' }}>{error}</span>
                    ) : (
                        <span>Loading…</span>
                    )}
                </div>
            )}
        </div>
    )
}

function resolveSource(
    sources: PlayRequestSources[],
    sourcePlayId: string,
    sourceIndex: number,
): PlayRequestSource {
    const reqSources = sources.find((s) => s.request.play_id === sourcePlayId)
    const pool: { request: PlayRequestSources['request']; source: PlaySource }[] = (
        reqSources ?? sources[0]
    ).sources.map((src) => ({
        request: (reqSources ?? sources[0]).request,
        source: src,
    }))

    const exact = pool.find((p) => p.source.index === sourceIndex)
    return exact ?? pool[0]
}
