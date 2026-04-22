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
import { parseLangKey } from '../utils/play-source.utils'
import { canPlayMediaType } from '../utils/video.utils'
import { PlayErrorHandler } from './player-error-handler'
import { HlsJsPlayer, hasNativeHls } from './player-hlsjs'
import { MediaEventHandler } from './player-media-events'
import { PlayerNativeSubtitles } from './player-native-subtitles'
import { AssSubtitle, SubtitleOffsetApplier } from './player-subtitles'
import {
    PlayerVideoControls,
    PlayerVideoInteractions,
    PlayerVideoStatus,
} from './player-video-controls'
import './player-video.css'
import type { PlayErrorType, VideoPlayerProps } from './player-video.types'

export const Player = createPlayer({ features: videoFeatures })
export type { PlayErrorEvent } from './player-video.types'

export function PlayerVideo({
    playRequestSource,
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    playRequestsSources,
    audioKey,
    forceTranscode,
    onSourceChange,
    onAudioKeyChange: onAudioChange,
    onForceTranscodeChange,
    onSubtitleKeyChange: onSubtitleChange,
    onPlayError,
    timeSliderStyle,
    defaultSubtitleKey,
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
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
    const [currentSubtitle, setCurrentSubtitleKey] = useState<
        string | undefined
    >(defaultSubtitleKey)
    const [subtitleOffset, setSubtitleOffset] = useState(0)
    const { data, isLoading, error, isRefetching } = useGetPlayServerMedia({
        playRequestSource,
        audio: audioKey,
        forceTranscode,
        ...playSettings.settings,
        ...(isSafari
            ? {
                  hlsIncludeAllSubtitles: true,
                  hlsSubtitleLang: defaultSubtitleKey,
              }
            : {}),
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

    const handleSubtitleChange = (key: string | undefined) => {
        setCurrentSubtitleKey(key)
        onSubtitleChange?.(key)
    }
    const currentSrc = data
        ? canDirectPlay && !isSafari
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
        setCurrentSubtitleKey(defaultSubtitleKey)
    }, [
        defaultSubtitleKey,
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

    useLayoutEffect(() => {
        if (media?.currentTime) {
            resumeTimeRef.current = media.currentTime
        }
    }, [data])

    useEffect(() => {
        setVideoLoading(true)
    }, [data])

    const subtitleStream = currentSubtitle
        ? playRequestSource.source.subtitles.find((s) => {
              const { lang, index } = parseLangKey(currentSubtitle)
              return s.language === lang && s.group_index === index
          })
        : undefined
    const canAdjustSubtitleOffset = !isSafari

    const isAssSubtitle =
        !isSafari &&
        (subtitleStream?.codec === 'ass' || subtitleStream?.codec === 'ssa')

    const subtitleUrl = currentSubtitle
        ? `${playRequestSource.request.play_url}/subtitle-file` +
          `?play_id=${playRequestSource.request.play_id}` +
          `&source_index=${playRequestSource.source.index}` +
          `&lang=${currentSubtitle}` +
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
        !isSafari && subtitleStream && !isAssSubtitle && subtitleUrl

    return (
        <Container className={`media-default-skin media-default-skin--video`}>
            {data && (
                <Video
                    src={videoSrc}
                    crossOrigin="anonymous"
                    playsInline
                    autoPlay
                >
                    {addTrackEnabled && (
                        <track
                            key={currentSubtitle}
                            kind="subtitles"
                            label={
                                subtitleStream.title || subtitleStream.language
                            }
                            srcLang={subtitleStream.language}
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
                        <HlsJsPlayer
                            src={data.hls_url}
                            startTimeRef={resumeTimeRef}
                        />
                    )}
                </Video>
            )}

            {canAdjustSubtitleOffset && currentSubtitle && !isAssSubtitle && (
                <SubtitleOffsetApplier offset={subtitleOffset} />
            )}
            <PlayerNativeSubtitles
                subtitleKey={currentSubtitle}
                isSafari={isSafari}
            />

            <PlayerVideoControls
                onClose={onClose}
                title={title}
                secondaryTitle={secondaryTitle}
                onPlayNext={onPlayNext}
                timeSliderStyle={timeSliderStyle}
                playRequestSource={playRequestSource}
                playRequestsSources={playRequestsSources}
                audio={audioKey}
                forceTranscode={forceTranscode}
                activeSubtitleKey={currentSubtitle}
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
