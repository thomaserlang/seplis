import type { Video as VideoMedia } from '@videojs/core'
import { Container, createPlayer, useMedia } from '@videojs/react'
import { Video, videoFeatures } from '@videojs/react/video'
import Hls from 'hls.js'
import {
    useEffect,
    useEffectEvent,
    useLayoutEffect,
    useRef,
    useState,
    type ReactNode,
} from 'react'
import { useGetPlayServerMedia } from '../api/play-server-request-media.api'
import { canPlayMediaType } from '../utils/video.utils'
import { PlayErrorHandler } from './player-error-handler'
import { HlsPlayer, hasNativeHls } from './player-hls'
import { MediaEventHandler } from './player-media-events'
import { AssSubtitle, SubtitleOffsetApplier } from './player-subtitles'
import {
    PlayerVideoControls,
    PlayerVideoInteractions,
    PlayerVideoStatus,
} from './player-video-controls'
import './player-video.css'
import type { PlayErrorType, VideoPlayerProps } from './player-video.types'

const STARTUP_TIMEOUT = 8_000

export const Player = createPlayer({ features: videoFeatures })
export type { PlayErrorEvent } from './player-video.types'

export function PlayerVideo({
    playRequestSource,
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    playRequestsSources,
    audio,
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
    const media = useMedia() as VideoMedia | null
    const resumeTimeRef = useRef<number>(defaultStartTime)
    const [videoLoading, setVideoLoading] = useState(true)
    const { data, isLoading, error, isRefetching } = useGetPlayServerMedia({
        playRequestSource,
        audio,
        forceTranscode,
        ...playSettings.settings,
        options: {
            refetchOnWindowFocus: false,
            // 6 hours
            staleTime: 6 * 60 * 60 * 1000,
        },
    })

    const canDirectPlay =
        data?.can_direct_play === true &&
        playRequestSource.source.media_type != null &&
        canPlayMediaType(playRequestSource.source.media_type)

    const needsHlsJs =
        data != null && !canDirectPlay && !hasNativeHls && Hls.isSupported()

    const [activeSubtitleKey, setActiveSubtitleKey] = useState<
        string | undefined
    >(defaultSubtitle)

    const handleSubtitleChange = (key: string | undefined) => {
        setActiveSubtitleKey(key)
        onSubtitleChange?.(key)
    }
    const [subtitleOffset, setSubtitleOffset] = useState(0)
    const currentSrc = data
        ? canDirectPlay
            ? data.direct_play_url
            : data.hls_url
        : undefined
    const videoSrc = needsHlsJs
        ? undefined
        : currentSrc
          ? `${currentSrc}#t=${resumeTimeRef.current}`
          : undefined
    const isPlayerLoading = videoLoading || isLoading || isRefetching

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

    useLayoutEffect(() => {
        if (media?.currentTime) {
            resumeTimeRef.current = media.currentTime
        }
    }, [data])

    useEffect(() => {
        setVideoLoading(true)
    }, [data])

    const activeSubtitle = activeSubtitleKey
        ? playRequestSource.source.subtitles.find((s) => {
              const [lang, idxStr] = activeSubtitleKey.split(':')
              return s.language === lang && s.index === parseInt(idxStr)
          })
        : undefined

    // TODO: JASSUB does not render in Safari, fall back to browser <track> for ASS/SSA
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
    const isAssSubtitle =
        !isSafari &&
        (activeSubtitle?.codec === 'ass' || activeSubtitle?.codec === 'ssa')

    const subtitleUrl = activeSubtitleKey
        ? `${playRequestSource.request.play_url}/subtitle-file` +
          `?play_id=${playRequestSource.request.play_id}` +
          `&source_index=${playRequestSource.source.index}` +
          `&lang=${activeSubtitleKey}` +
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
    useEffect(() => {
        if (!currentSrc || isLoading || isRefetching || !videoLoading) return

        const timeoutId = window.setTimeout(() => {
            emitPlayError('stall_timeout')
        }, STARTUP_TIMEOUT)

        return () => {
            window.clearTimeout(timeoutId)
        }
    }, [currentSrc, emitPlayError, isLoading, isRefetching, videoLoading])

    return (
        <Container className={`media-default-skin media-default-skin--video`}>
            {data && (
                <Video
                    src={videoSrc}
                    crossOrigin="anonymous"
                    playsInline
                    autoPlay
                >
                    {activeSubtitle && !isAssSubtitle && subtitleUrl && (
                        <track
                            key={activeSubtitleKey}
                            kind="subtitles"
                            label={
                                activeSubtitle.title || activeSubtitle.language
                            }
                            srcLang={activeSubtitle.language}
                            src={subtitleUrl}
                            default
                        />
                    )}
                    {isAssSubtitle && subtitleUrl && (
                        <AssSubtitle
                            subUrl={subtitleUrl}
                            offset={subtitleOffset}
                        />
                    )}
                    {needsHlsJs && (
                        <HlsPlayer
                            src={data.hls_url}
                            startTimeRef={resumeTimeRef}
                        />
                    )}
                </Video>
            )}

            {activeSubtitleKey && !isAssSubtitle && (
                <SubtitleOffsetApplier offset={subtitleOffset} />
            )}

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
                activeSubtitleKey={activeSubtitleKey}
                subtitleOffset={subtitleOffset}
                onSourceChange={onSourceChange}
                onAudioChange={onAudioChange}
                onForceTranscodeChange={onForceTranscodeChange}
                onSubtitleChange={handleSubtitleChange}
                onSubtitleOffsetChange={setSubtitleOffset}
                preferredAudioLangs={preferredAudioLangs}
                preferredSubtitleLangs={preferredSubtitleLangs}
                playSettings={playSettings}
            />

            <PlayerVideoStatus
                isPlayerLoading={isPlayerLoading}
                error={error}
                hasData={data != null}
                isLoading={isLoading}
                onClose={onClose}
            />

            <MediaEventHandler
                onVideoReady={onVideoReady}
                onVideoError={onVideoError}
                onTimeUpdate={(currentTime, duration) => {
                    onTimeUpdate?.(currentTime, duration)
                    if (videoLoading) {
                        setVideoLoading(false)
                    }
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
