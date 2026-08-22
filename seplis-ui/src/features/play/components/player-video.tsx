import { Container, createPlayer } from '@videojs/react'
import { HlsJsVideo } from '@videojs/react/media/hlsjs-video'
import { Video, videoFeatures } from '@videojs/react/video'
import {
    useEffect,
    useEffectEvent,
    useRef,
    useState,
    type ReactNode,
} from 'react'
import { useGetPlayServerMedia } from '../api/play-server-request-media.api'
import { PlaySourceStream } from '../types/play-source.types'
import { toLangKey } from '../utils/play-source.utils'
import { canPlayMediaType } from '../utils/video.utils'
import { PlayerVideoInteractions, PlayerVideoStatus } from './player-controls'
import { PlayErrorHandler } from './player-error-handler'
import { MediaEventHandler } from './player-media-events'
import { PlayerNativeSubtitles } from './player-native-subtitles'
import { AssSubtitle, SubtitleOffsetApplier } from './player-subtitles'
import { PlayerVideoControls } from './player-video-controls'
import './player-video.css'
import type { PlayErrorType, VideoPlayerProps } from './player-video.types'

export const { Player } = createPlayer({ features: videoFeatures })
export type { PlayErrorEvent } from './player-video.types'

export function PlayerVideo({
    playRequestSource,
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    playRequestsSources,
    audio: audio,
    forceTranscode,
    onSourceChange,
    onAudioChange,
    onForceTranscodeChange,
    onSubtitleChange,
    onPlayError,
    timeSliderStyle,
    defaultSubtitle,
    preferredAudioLangs,
    preferredSubtitleLangs,
    defaultStartTime = 0,
    onVideoReady,
    onVideoError,
    onTimeUpdate,
    playSettings,
}: VideoPlayerProps): ReactNode {
    const resumeTimeRef = useRef<number>(defaultStartTime)
    const [videoLoading, setVideoLoading] = useState(true)
    const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(
        null,
    )
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
    const [subtitle, setCurrentSubtitle] = useState<
        PlaySourceStream | undefined
    >(defaultSubtitle)
    const [subtitleOffset, setSubtitleOffset] = useState(0)
    const { data, isLoading, error, isRefetching } = useGetPlayServerMedia({
        playRequestSource,
        audio: toLangKey(audio),
        forceTranscode,
        ...playSettings.settings,
        ...(isSafari
            ? {
                  hlsIncludeAllSubtitles: true,
                  hlsSubtitleLang: toLangKey(defaultSubtitle),
              }
            : {}),
        options: {
            refetchOnWindowFocus: false,
            // 6 hours
            staleTime: 6 * 60 * 60 * 1000,
            // The URLs belong to a session that is closed on unmount.
            gcTime: 0,
        },
    })

    const canDirectPlay =
        data?.can_direct_play === true &&
        playRequestSource.source.media_type != null &&
        canPlayMediaType(playRequestSource.source.media_type)

    const handleSubtitleChange = (source?: PlaySourceStream) => {
        setCurrentSubtitle(source)
        onSubtitleChange?.(source)
    }
    const useHls = data != null && (!canDirectPlay || isSafari)
    const currentSrc = data
        ? useHls
            ? data.hls_url
            : data.direct_play_url
        : undefined
    const playbackTransport = data
        ? canDirectPlay && !isSafari
            ? 'direct_play'
            : 'hls'
        : undefined
    const isPlayerLoading = videoLoading || isLoading || isRefetching

    useEffect(() => {
        setCurrentSubtitle(defaultSubtitle)
    }, [
        defaultSubtitle,
        playRequestSource.request.play_id,
        playRequestSource.source.index,
    ])

    useEffect(() => {
        if (!data) return

        const id = setInterval(() => {
            fetch(data.keep_alive_url)
                .then((response) => {
                    if (response.status === 404) {
                        clearInterval(id)
                    }
                })
                .catch(() => {})
        }, 5000)
        return () => {
            clearInterval(id)
            fetch(data.close_session_url).catch(() => {})
        }
    }, [data])

    useEffect(() => {
        setVideoLoading(true)
    }, [currentSrc])

    const canAdjustSubtitleOffset = !isSafari

    const isAssSubtitle =
        !isSafari && (subtitle?.codec === 'ass' || subtitle?.codec === 'ssa')

    const subtitleUrl = subtitle
        ? `${playRequestSource.request.play_url}/subtitle-file` +
          `?play_id=${playRequestSource.request.play_id}` +
          `&source_index=${playRequestSource.source.index}` +
          `&lang=${toLangKey(subtitle)}` +
          (isAssSubtitle ? `&output_format=ass` : '')
        : undefined
    const playErrorCountsRef = useRef<Record<PlayErrorType, number>>({
        stall_timeout: 0,
    })
    useEffect(() => {
        playErrorCountsRef.current = {
            stall_timeout: 0,
        }
    }, [currentSrc])

    const emitPlayError = useEffectEvent((type: PlayErrorType) => {
        playErrorCountsRef.current[type]++
        onPlayError?.({ type, count: playErrorCountsRef.current[type] })
    })
    const addTrackEnabled =
        !isSafari && subtitle && !isAssSubtitle && subtitleUrl

    return (
        <Container className={`media-default-skin media-default-skin--video`}>
            {data && (
                <MediaVideo
                    src={currentSrc!}
                    useHlsJs={useHls && !isSafari}
                    videoRef={setVideoElement}
                >
                    {addTrackEnabled && (
                        <track
                            key={toLangKey(subtitle)}
                            kind="subtitles"
                            label={subtitle.title || subtitle.language}
                            srcLang={subtitle.language}
                            src={subtitleUrl}
                            default
                        />
                    )}
                    {isAssSubtitle && subtitleUrl && videoElement && (
                        <AssSubtitle
                            video={videoElement}
                            subUrl={subtitleUrl}
                            offset={subtitleOffset}
                        />
                    )}
                </MediaVideo>
            )}

            {canAdjustSubtitleOffset && subtitle && !isAssSubtitle && (
                <SubtitleOffsetApplier offset={subtitleOffset} />
            )}
            <PlayerNativeSubtitles subtitle={subtitle} isSafari={isSafari} />

            <PlayerVideoControls
                onClose={onClose}
                title={title}
                secondaryTitle={secondaryTitle}
                onPlayNext={onPlayNext}
                timeSliderStyle={timeSliderStyle}
                playRequestSource={playRequestSource}
                playRequestsSources={playRequestsSources}
                audio={audio}
                forceTranscode={forceTranscode}
                subtitle={subtitle}
                subtitleOffset={subtitleOffset}
                canAdjustSubtitleOffset={canAdjustSubtitleOffset}
                onSourceChange={onSourceChange}
                onAudioChange={onAudioChange}
                onForceTranscodeChange={onForceTranscodeChange}
                onSubtitleChange={handleSubtitleChange}
                onSubtitleOffsetChange={setSubtitleOffset}
                preferredAudioLangs={preferredAudioLangs}
                preferredSubtitleLangs={preferredSubtitleLangs}
                playSettings={playSettings}
                transcodeDecision={data?.transcode_decision}
                playbackTransport={playbackTransport}
            />

            <PlayerVideoStatus
                isPlayerLoading={isPlayerLoading}
                error={error}
                hasData={data != null}
                isLoading={isLoading}
                onClose={onClose}
            />

            <MediaEventHandler
                onVideoReady={() => {
                    setVideoLoading(false)
                    onVideoReady?.()
                }}
                onVideoError={onVideoError}
                onTimeUpdate={(currentTime, duration) => {
                    resumeTimeRef.current = currentTime
                    onTimeUpdate?.(currentTime, duration)
                }}
                startTime={resumeTimeRef.current}
            />

            {data && (
                <PlayErrorHandler
                    src={currentSrc}
                    isMediaLoading={isLoading || isRefetching}
                    onPlayError={emitPlayError}
                />
            )}
            <div className="media-overlay" />

            <PlayerVideoInteractions />
        </Container>
    )
}

function MediaVideo({
    src,
    useHlsJs,
    children,
    videoRef,
}: {
    src: string
    useHlsJs: boolean
    children: ReactNode
    videoRef?: (element: HTMLVideoElement | null) => void
}) {
    const props = {
        crossOrigin: 'anonymous' as const,
        playsInline: true,
        autoPlay: true,
    }

    return useHlsJs ? (
        <HlsJsVideo {...props} ref={videoRef} source={{ src }}>
            {children}
        </HlsJsVideo>
    ) : (
        <Video {...props} ref={videoRef} src={src}>
            {children}
        </Video>
    )
}
