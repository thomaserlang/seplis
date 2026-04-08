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
import {
    useEffect,
    useEffectEvent,
    useState,
    type CSSProperties,
    type ReactNode,
} from 'react'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlayServerMedia,
} from '../types/play-source.types'
import { AirPlayButton, Button, VolumePopover } from './player-controls'
import { SettingsPopover } from './player-settings'

import './player-video.css'

const SEEK_TIME = 10

export const Player = createPlayer({ features: videoFeatures })

export interface VideoPlayerProps {
    playRequestSource: PlayRequestSource
    playServerMedia: PlayServerMedia
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    playRequestsSources: PlayRequestSources[]
    maxBitrate: number
    audio: string | undefined
    forceTranscode: boolean
    onSourceChange: (source: PlayRequestSource) => void
    onBitrateChange: (bitrate: number) => void
    onAudioChange: (audio: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange?: (subtitle: string | undefined) => void
    timeSliderStyle?: CSSProperties
    isVideoLoading?: boolean
    suppressErrorDialog?: boolean
    defaultSubtitle?: string
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    defaultStartTime?: number
}

export function PlayerVideo({
    playRequestSource,
    playServerMedia,
    title,
    secondaryTitle,
    onClose,
    playRequestsSources,
    maxBitrate,
    audio,
    forceTranscode,
    onSourceChange,
    onBitrateChange,
    onAudioChange,
    onForceTranscodeChange,
    onSubtitleChange,
    timeSliderStyle,
    isVideoLoading,
    suppressErrorDialog,
    defaultSubtitle,
    preferredAudioLangs,
    preferredSubtitleLangs,
    defaultStartTime,
}: VideoPlayerProps): ReactNode {
    const [activeSubtitleKey, setActiveSubtitleKey] = useState<
        string | undefined
    >(defaultSubtitle)

    const handleSubtitleChange = (key: string | undefined) => {
        setActiveSubtitleKey(key)
        onSubtitleChange?.(key)
    }
    const [subtitleOffset, setSubtitleOffset] = useState(0)

    useEffect(() => {
        const id = setInterval(() => {
            fetch(playServerMedia.keep_alive_url).catch(() => {})
        }, 5000)
        return () => clearInterval(id)
    }, [playServerMedia.keep_alive_url])

    const activeSubtitle = activeSubtitleKey
        ? playRequestSource.source.subtitles.find((s) => {
              const [lang, idxStr] = activeSubtitleKey.split(':')
              return s.language === lang && s.index === parseInt(idxStr)
          })
        : undefined

    return (
        <Container className={`media-default-skin media-default-skin--video`}>
            <Video
                src={
                    (playServerMedia.can_direct_play
                        ? playServerMedia.direct_play_url
                        : playServerMedia.hls_url) +
                    `#t=${defaultStartTime || 0}`
                }
                crossOrigin="anonymous"
            >
                {activeSubtitle && (
                    <track
                        key={activeSubtitleKey}
                        kind="subtitles"
                        label={activeSubtitle.title || activeSubtitle.language}
                        srcLang={activeSubtitle.language}
                        src={
                            `${playRequestSource.request.play_url}/subtitle-file` +
                            `?play_id=${playRequestSource.request.play_id}` +
                            `&source_index=${playRequestSource.source.index}` +
                            `&offset=0` +
                            `&lang=${activeSubtitleKey}`
                        }
                        default
                    />
                )}
            </Video>

            {activeSubtitleKey && (
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
                        <div className="media-surface">
                            <PageLoader />
                        </div>
                    </div>
                )}
            />

            {isVideoLoading && (
                <div className="media-buffering-indicator" data-visible="">
                    <div className="media-surface">
                        <PageLoader />
                    </div>
                </div>
            )}

            {!suppressErrorDialog && (
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
                            currentPlayRequestSource={playRequestSource}
                            playRequestsSources={playRequestsSources}
                            maxBitrate={maxBitrate}
                            audioLang={audio}
                            forceTranscode={forceTranscode}
                            activeSubtitleKey={activeSubtitleKey}
                            subtitleOffset={subtitleOffset}
                            onSourceChange={onSourceChange}
                            onBitrateChange={onBitrateChange}
                            onAudioLangChange={onAudioChange}
                            onForceTranscodeChange={onForceTranscodeChange}
                            onSubtitleChange={handleSubtitleChange}
                            onSubtitleOffsetChange={setSubtitleOffset}
                            preferredAudioLangs={preferredAudioLangs}
                            preferredSubtitleLangs={preferredSubtitleLangs}
                        />

                        <AirPlayButton />

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

            <VideoClickHandler />
            <div className="media-overlay" />
        </Container>
    )
}

function SubtitleOffsetApplier({ offset }: { offset: number }): ReactNode {
    const media = useMedia()

    useEffect(() => {
        if (!media) return
        const tracks = media.textTracks
        for (let i = 0; i < tracks.length; i++) {
            const track = tracks[i]
            if (track.kind !== 'subtitles' || !track.cues) continue
            for (let j = 0; j < track.cues.length; j++) {
                const cue = track.cues[j]
                if (!('_originalStart' in cue)) {
                    ;(cue as any)._originalStart = cue.startTime
                    ;(cue as any)._originalEnd = cue.endTime
                }
                cue.startTime = (cue as any)._originalStart + offset
                cue.endTime = (cue as any)._originalEnd + offset
            }
        }
    }, [media, offset])

    return null
}

function VideoClickHandler(): ReactNode {
    const media = useMedia()

    const togglePlayback = useEffectEvent(() => {
        if (!media) return
        if (media.paused) {
            media.play()
        } else {
            media.pause()
        }
    })

    const handleKeyDown = useEffectEvent((e: KeyboardEvent) => {
        if (
            e.target instanceof HTMLInputElement ||
            e.target instanceof HTMLTextAreaElement
        )
            return

        if (e.code === 'Space') {
            e.preventDefault()
            togglePlayback()
        } else if (e.code === 'ArrowLeft') {
            e.preventDefault()
            if (media)
                media.currentTime = Math.max(0, media.currentTime - SEEK_TIME)
        } else if (e.code === 'ArrowRight') {
            e.preventDefault()
            if (media) media.currentTime += SEEK_TIME
        }
    })

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown)
        return () => document.removeEventListener('keydown', handleKeyDown)
    }, [])

    return (
        <div
            className="media-click-handler"
            style={{
                position: 'absolute',
                inset: 0,
                cursor: 'pointer',
                zIndex: 1,
            }}
            onClick={togglePlayback}
        />
    )
}
