import { PageLoader } from '@/components/page-loader'
import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    ArrowLeftIcon,
    CornersInIcon,
    CornersOutIcon,
    PauseIcon,
    PictureInPictureIcon,
    PlayIcon,
} from '@phosphor-icons/react'
import {
    BufferingIndicator,
    Container,
    Controls,
    ErrorDialog,
    FullscreenButton,
    MediaGesture,
    MediaHotkey,
    PiPButton,
    PlayButton,
    PlaybackRateButton,
    SeekButton,
    Time,
    TimeSlider,
    Tooltip,
    createPlayer,
    useMedia,
} from '@videojs/react'
import { Video, videoFeatures } from '@videojs/react/video'
import JASSUB from 'jassub'
import {
    useEffect,
    useEffectEvent,
    useLayoutEffect,
    useRef,
    useState,
    type CSSProperties,
    type ReactNode,
} from 'react'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'
import {
    AirPlayButton,
    Button,
    ChromecastButton,
    VolumePopover,
} from './player-controls'

import type { Video as VideoMedia } from '@videojs/core'
import Hls from 'hls.js'
import { useGetPlayServerMedia } from '../api/play-server-request-media.api'
import { UsePlaySettings } from '../hooks/use-play-settings'
import { SettingsPopover } from './player-controls/settings-popover'
import { PlayerError } from './player-error'
import './player-video.css'

const SEEK_TIME = 10
const STALL_LOAD_TIMEOUT = 10_000

export type PlayErrorType = 'load_timeout' | 'stall_timeout'

export interface PlayErrorEvent {
    type: PlayErrorType
    count: number
}

export const Player = createPlayer({ features: videoFeatures })

export interface VideoPlayerProps {
    playRequestSource: PlayRequestSource
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    playRequestsSources: PlayRequestSources[]
    audio: string | undefined
    forceTranscode: boolean
    onSourceChange: (source: PlayRequestSource) => void
    onAudioChange: (audio: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange?: (subtitle: string | undefined) => void
    onPlayError?: (event: PlayErrorEvent) => void
    timeSliderStyle?: CSSProperties
    defaultSubtitle?: string
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    defaultStartTime?: number
    onVideoReady?: () => void
    onVideoError?: () => void
    onTimeUpdate?: (currentTime: number, duration: number) => void
    playSettings: UsePlaySettings
}

export function PlayerVideo({
    playRequestSource,
    title,
    secondaryTitle,
    onClose,
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
    const resumtimeRef = useRef<number>(defaultStartTime)
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

    const needsHlsJs =
        data != null &&
        !data.can_direct_play &&
        !hasNativeHls &&
        Hls.isSupported()

    const [activeSubtitleKey, setActiveSubtitleKey] = useState<
        string | undefined
    >(defaultSubtitle)

    const handleSubtitleChange = (key: string | undefined) => {
        setActiveSubtitleKey(key)
        onSubtitleChange?.(key)
    }
    const [subtitleOffset, setSubtitleOffset] = useState(0)

    useEffect(() => {
        if (!data?.keep_alive_url) return
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
    }, [data?.keep_alive_url || ''])

    useLayoutEffect(() => {
        if (media?.currentTime) {
            resumtimeRef.current = media.currentTime
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

    return (
        <Container className={`media-default-skin media-default-skin--video`}>
            {data && (
                <Video
                    src={
                        needsHlsJs
                            ? undefined
                            : `${
                                  data.can_direct_play
                                      ? data.direct_play_url
                                      : data.hls_url
                              }#t=${resumtimeRef.current}`
                    }
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
                            startTimeRef={resumtimeRef}
                        />
                    )}
                </Video>
            )}

            {activeSubtitleKey && !isAssSubtitle && (
                <SubtitleOffsetApplier offset={subtitleOffset} />
            )}

            <Controls.Root className="media-header">
                {onClose && (
                    <button
                        type="button"
                        className="media-button media-button--subtle media-button--icon media-header__close"
                        onClick={onClose}
                        aria-label="Close player"
                    >
                        <ArrowLeftIcon className="media-icon" weight="bold" />
                    </button>
                )}
                {title && (
                    <div className="media-header__info">
                        <span className="media-header__title">{title}</span>
                        {secondaryTitle && (
                            <span className="media-header__secondaryTitle">
                                {secondaryTitle}
                            </span>
                        )}
                    </div>
                )}
            </Controls.Root>

            <BufferingIndicator
                render={() => (
                    <div className="media-buffering-indicator">
                        <PageLoader />
                    </div>
                )}
            />

            {(isLoading || isRefetching || videoLoading) && (
                <div className="media-buffering-indicator" data-visible="">
                    <PageLoader />
                </div>
            )}

            <ErrorDialog.Root>
                <ErrorDialog.Popup className="media-error">
                    <div className="media-error__dialog media-surface">
                        <div className="media-error__content">
                            <ErrorDialog.Title className="media-error__title">
                                Something went wrong.
                            </ErrorDialog.Title>
                            <ErrorDialog.Description className="media-error__description" />
                        </div>
                        <div className="media-error__actions">
                            {onClose && (
                                <ErrorDialog.Close
                                    className="media-button media-button--subtle"
                                    onClick={onClose}
                                >
                                    Go Back
                                </ErrorDialog.Close>
                            )}
                            <ErrorDialog.Close
                                className="media-button media-button--primary"
                                onClick={() => window.location.reload()}
                            >
                                Refresh
                            </ErrorDialog.Close>
                        </div>
                    </div>
                </ErrorDialog.Popup>
            </ErrorDialog.Root>

            {error && (
                <PlayerError
                    title="Something went wrong on the play server"
                    errorObj={error}
                />
            )}

            {!data && !isLoading && !error && (
                <PlayerError title="No playable source found" />
            )}

            <Controls.Root className="media-surface media-controls">
                <Tooltip.Provider>
                    <div className="media-button-group">
                        <Tooltip.Root side="top">
                            <Tooltip.Trigger
                                render={
                                    <PlayButton
                                        className="media-button--play"
                                        render={<Button />}
                                    >
                                        <ArrowCounterClockwiseIcon
                                            className="media-icon media-icon--restart"
                                            weight="bold"
                                        />
                                        <PlayIcon
                                            className="media-icon media-icon--play"
                                            weight="fill"
                                        />
                                        <PauseIcon
                                            className="media-icon media-icon--pause"
                                            weight="fill"
                                        />
                                    </PlayButton>
                                }
                            />
                            <Tooltip.Popup className="media-surface media-tooltip" />
                        </Tooltip.Root>

                        <Tooltip.Root side="top">
                            <Tooltip.Trigger
                                render={
                                    <SeekButton
                                        seconds={-SEEK_TIME}
                                        className="media-button--seek"
                                        render={<Button />}
                                    >
                                        <ArrowCounterClockwiseIcon
                                            className="media-icon media-icon--seek"
                                            weight="bold"
                                        />
                                    </SeekButton>
                                }
                            />
                            <Tooltip.Popup className="media-surface media-tooltip">
                                Seek backward {SEEK_TIME} seconds
                            </Tooltip.Popup>
                        </Tooltip.Root>

                        <Tooltip.Root side="top">
                            <Tooltip.Trigger
                                render={
                                    <SeekButton
                                        seconds={SEEK_TIME}
                                        className="media-button--seek"
                                        render={<Button />}
                                    >
                                        <ArrowClockwiseIcon
                                            className="media-icon media-icon--seek"
                                            weight="bold"
                                        />
                                    </SeekButton>
                                }
                            />
                            <Tooltip.Popup className="media-surface media-tooltip">
                                Seek forward {SEEK_TIME} seconds
                            </Tooltip.Popup>
                        </Tooltip.Root>
                    </div>

                    <div className="media-time-controls">
                        <Time.Value type="current" className="media-time" />
                        <TimeSlider.Root
                            className="media-slider"
                            style={timeSliderStyle}
                        >
                            <TimeSlider.Track className="media-slider__track">
                                <TimeSlider.Fill className="media-slider__fill" />
                                <TimeSlider.Buffer className="media-slider__buffer" />
                            </TimeSlider.Track>
                            <TimeSlider.Thumb className="media-slider__thumb" />
                            <TimeSlider.Thumb className="react-time-slider-parts__thumb" />

                            <div className="media-surface media-preview media-slider__preview">
                                <TimeSlider.Value
                                    type="pointer"
                                    className="media-time media-preview__time"
                                />
                            </div>
                        </TimeSlider.Root>
                        <Time.Value type="duration" className="media-time" />
                    </div>

                    <div
                        className="media-button-group"
                        style={{ marginLeft: 'auto' }}
                    >
                        <Tooltip.Root side="top">
                            <Tooltip.Trigger
                                render={
                                    <PlaybackRateButton
                                        className="media-button--playback-rate"
                                        render={<Button />}
                                    />
                                }
                            />
                            <Tooltip.Popup className="media-surface media-tooltip">
                                Toggle playback rate
                            </Tooltip.Popup>
                        </Tooltip.Root>

                        <VolumePopover />

                        <SettingsPopover
                            playRequestSource={playRequestSource}
                            playRequestsSources={playRequestsSources}
                            audioLang={audio}
                            forceTranscode={forceTranscode}
                            activeSubtitleKey={activeSubtitleKey}
                            subtitleOffset={subtitleOffset}
                            onSourceChange={onSourceChange}
                            onAudioLangChange={onAudioChange}
                            onForceTranscodeChange={onForceTranscodeChange}
                            onSubtitleChange={handleSubtitleChange}
                            onSubtitleOffsetChange={setSubtitleOffset}
                            preferredAudioLangs={preferredAudioLangs}
                            preferredSubtitleLangs={preferredSubtitleLangs}
                            playSettings={playSettings}
                        />

                        <AirPlayButton />
                        <ChromecastButton />

                        <Tooltip.Root side="top">
                            <Tooltip.Trigger
                                render={
                                    <PiPButton
                                        className="media-button--pip"
                                        render={<Button />}
                                    >
                                        <PictureInPictureIcon
                                            className="media-icon media-icon--pip-enter"
                                            weight="regular"
                                        />
                                        <PictureInPictureIcon
                                            className="media-icon media-icon--pip-exit"
                                            weight="fill"
                                        />
                                    </PiPButton>
                                }
                            />
                            <Tooltip.Popup className="media-surface media-tooltip" />
                        </Tooltip.Root>

                        <Tooltip.Root side="top">
                            <Tooltip.Trigger
                                render={
                                    <FullscreenButton
                                        className="media-button--fullscreen"
                                        render={<Button />}
                                    >
                                        <CornersOutIcon
                                            className="media-icon media-icon--fullscreen-enter"
                                            weight="bold"
                                        />
                                        <CornersInIcon
                                            className="media-icon media-icon--fullscreen-exit"
                                            weight="bold"
                                        />
                                    </FullscreenButton>
                                }
                            />
                            <Tooltip.Popup className="media-surface media-tooltip" />
                        </Tooltip.Root>
                    </div>
                </Tooltip.Provider>
            </Controls.Root>

            <MediaEventHandler
                onVideoReady={onVideoReady}
                onVideoError={onVideoError}
                onTimeUpdate={(currentTime, duration) => {
                    onTimeUpdate?.(currentTime, duration)
                    if (videoLoading) {
                        setVideoLoading(false)
                    }
                }}
                startTime={resumtimeRef.current}
            />

            {data && (
                <PlayErrorHandler
                    src={data.hls_url}
                    onPlayError={onPlayError}
                />
            )}
            <div className="media-overlay" />

            <MediaHotkey keys="Space" action="togglePaused" target="document" />
            <MediaHotkey keys="k" action="togglePaused" target="document" />
            <MediaHotkey keys="m" action="toggleMuted" target="document" />
            <MediaHotkey keys="f" action="toggleFullscreen" target="document" />
            <MediaHotkey keys="c" action="toggleSubtitles" target="document" />
            <MediaHotkey
                keys="i"
                action="togglePictureInPicture"
                target="document"
            />
            <MediaHotkey keys="ArrowRight" action="seekStep" value={5} />
            <MediaHotkey keys="ArrowLeft" action="seekStep" value={-5} />
            <MediaHotkey keys="l" action="seekStep" value={10} />
            <MediaHotkey keys="j" action="seekStep" value={-10} />
            <MediaHotkey keys="ArrowUp" action="volumeStep" value={0.05} />
            <MediaHotkey keys="ArrowDown" action="volumeStep" value={-0.05} />
            <MediaHotkey keys="0-9" action="seekToPercent" target="document" />
            <MediaHotkey
                keys="Home"
                action="seekToPercent"
                value={0}
                target="document"
            />
            <MediaHotkey
                keys="End"
                action="seekToPercent"
                value={100}
                target="document"
            />
            <MediaHotkey keys=">" action="speedUp" target="document" />
            <MediaHotkey keys="<" action="speedDown" target="document" />

            <MediaGesture
                type="tap"
                action="togglePaused"
                pointer="mouse"
                region="center"
            />
            <MediaGesture type="tap" action="toggleControls" pointer="touch" />
            <MediaGesture
                type="doubletap"
                action="seekStep"
                value={-10}
                region="left"
            />
            <MediaGesture
                type="doubletap"
                action="toggleFullscreen"
                region="center"
            />
            <MediaGesture
                type="doubletap"
                action="seekStep"
                value={10}
                region="right"
            />
        </Container>
    )
}

const hasNativeHls = (() => {
    const video = document.createElement('video')
    return !!video.canPlayType('application/vnd.apple.mpegurl')
})()

function MediaEventHandler({
    onVideoReady,
    onVideoError,
    onTimeUpdate,
    startTime,
}: {
    onVideoReady?: () => void
    onVideoError?: () => void
    onTimeUpdate?: (currentTime: number, duration: number) => void
    startTime: number
}): null {
    const media = useMedia() as VideoMedia | null
    const resumtimeRef = useRef<number>(startTime)
    resumtimeRef.current = startTime

    useEffect(() => {
        if (!media) return

        const handleCanPlay = () => onVideoReady?.()
        const handleError = () => onVideoError?.()
        const handleTimeUpdate = () => {
            if (!media.duration) return
            onTimeUpdate?.(media.currentTime, media.duration)
        }
        const handleVolumeChange = () => {
            localStorage.setItem(
                'player-volume',
                String(Math.round(media.volume * 100) / 100),
            )
        }
        const handleMetadataLoaded = () => {
            media.currentTime = resumtimeRef.current
        }
        const handleSeeked = () => {
            if (media.paused) media.play().catch(() => {})
        }

        const savedVolume = localStorage.getItem('player-volume')
        media.volume = savedVolume !== null ? parseFloat(savedVolume) : 0.5

        media.addEventListener('canplay', handleCanPlay)
        media.addEventListener('error', handleError)
        media.addEventListener('timeupdate', handleTimeUpdate)
        media.addEventListener('volumechange', handleVolumeChange)
        media.addEventListener('loadedmetadata', handleMetadataLoaded)
        media.addEventListener('seeked', handleSeeked)

        return () => {
            media.removeEventListener('canplay', handleCanPlay)
            media.removeEventListener('error', handleError)
            media.removeEventListener('timeupdate', handleTimeUpdate)
            media.removeEventListener('volumechange', handleVolumeChange)
            media.removeEventListener('loadedmetadata', handleMetadataLoaded)
            media.removeEventListener('seeked', handleSeeked)
        }
    }, [media])

    return null
}

function AssSubtitle({
    subUrl,
    offset,
}: {
    subUrl: string
    offset: number
}): ReactNode {
    const media = useMedia() as VideoMedia | null
    const jassubRef = useRef<JASSUB | null>(null)

    useEffect(() => {
        if (!media) return
        const jassub = new JASSUB({
            video: media as unknown as HTMLVideoElement,
            subUrl,
        })
        jassubRef.current = jassub
        return () => {
            jassub.destroy()
            jassubRef.current = null
        }
    }, [media, subUrl])

    useEffect(() => {
        if (jassubRef.current) jassubRef.current.timeOffset = offset
    }, [offset])

    return null
}

function SubtitleOffsetApplier({ offset }: { offset: number }): ReactNode {
    const media = useMedia() as VideoMedia | null

    useEffect(() => {
        if (!media) return
        const tracks = media.textTracks
        for (let i = 0; i < tracks.length; i++) {
            const track = tracks[i]
            if (track.kind !== 'subtitles' || !track.cues) continue
            for (const cue of track.cues) {
                if (!('_originalStart' in cue)) {
                    ;(cue as any)._originalStart = cue.startTime
                    ;(cue as any)._originalEnd = cue.endTime
                }
                ;(cue as any).startTime = (cue as any)._originalStart + offset
                ;(cue as any).endTime = (cue as any)._originalEnd + offset
            }
        }
    }, [media, offset])

    return null
}

function PlayErrorHandler({
    src,
    onPlayError,
}: {
    src: string | undefined
    onPlayError?: (event: PlayErrorEvent) => void
}): null {
    const media = useMedia() as VideoMedia | null
    const loadTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(
        undefined,
    )
    const stallTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(
        undefined,
    )
    const countsRef = useRef<Record<PlayErrorType, number>>({
        load_timeout: 0,
        stall_timeout: 0,
    })

    const fireError = useEffectEvent((type: PlayErrorType) => {
        countsRef.current[type]++
        onPlayError?.({ type, count: countsRef.current[type] })
    })

    useEffect(() => {
        clearTimeout(loadTimeoutRef.current)
        loadTimeoutRef.current = setTimeout(
            () => fireError('load_timeout'),
            STALL_LOAD_TIMEOUT,
        )
        return () => clearTimeout(loadTimeoutRef.current)
    }, [src])

    useEffect(() => {
        if (!media) return
        const onWaiting = () => {
            clearTimeout(stallTimeoutRef.current)
            stallTimeoutRef.current = setTimeout(
                () => fireError('stall_timeout'),
                STALL_LOAD_TIMEOUT,
            )
        }
        const onPlaying = () => clearTimeout(stallTimeoutRef.current)
        const clearAll = () => {
            clearTimeout(loadTimeoutRef.current)
            clearTimeout(stallTimeoutRef.current)
        }
        media.addEventListener('waiting', onWaiting)
        media.addEventListener('playing', onPlaying)
        media.addEventListener('canplay', clearAll)
        media.addEventListener('error', clearAll)
        return () => {
            media.removeEventListener('waiting', onWaiting)
            media.removeEventListener('playing', onPlaying)
            media.removeEventListener('canplay', clearAll)
            media.removeEventListener('error', clearAll)
        }
    }, [media])

    return null
}

function HlsPlayer({
    src,
    startTimeRef,
}: {
    src: string
    startTimeRef: { current: number }
}): null {
    const media = useMedia() as VideoMedia | null

    useEffect(() => {
        if (!media) return
        const hls = new Hls({ startPosition: startTimeRef.current })
        hls.loadSource(src)
        hls.attachMedia(media as unknown as HTMLVideoElement)
        return () => {
            hls.destroy()
        }
    }, [media, src])

    return null
}
