import { PageLoader } from '@/components/page-loader'
import { Loader } from '@mantine/core'
import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    ArrowLeftIcon,
    ClosedCaptioningIcon,
    CornersInIcon,
    CornersOutIcon,
    PauseIcon,
    PictureInPictureIcon,
    PlayIcon,
    SpeakerHighIcon,
    SpeakerLowIcon,
    SpeakerXIcon,
} from '@phosphor-icons/react'
import {
    BufferingIndicator,
    CaptionsButton,
    Container,
    Controls,
    ErrorDialog,
    FullscreenButton,
    MuteButton,
    PiPButton,
    PlayButton,
    PlaybackRateButton,
    Popover,
    SeekButton,
    Slider,
    Time,
    TimeSlider,
    Tooltip,
    VolumeSlider,
    createPlayer,
    usePlayer,
} from '@videojs/react'
import { Video, videoFeatures } from '@videojs/react/video'
import { forwardRef, type ComponentProps, type ReactNode } from 'react'
import { PlayServerMedia } from '../types/play-source.types'
import './player-video.css'

// ================================================================
// Player
// ================================================================

const SEEK_TIME = 10

export const Player = createPlayer({ features: videoFeatures })

export interface VideoPlayerProps {
    media: PlayServerMedia
    title?: string
    subtitle?: string
    onClose?: () => void
}

export function PlayerVideo({
    media,
    title,
    subtitle,
    onClose,
}: VideoPlayerProps): ReactNode {
    return (
        <Player.Provider>
            <Container
                className={`media-default-skin media-default-skin--video`}
            >
                <Video src={media.hls_url} autoPlay />

                <Controls.Root className="media-header">
                    {onClose && (
                        <button
                            type="button"
                            className="media-button media-button--subtle media-button--icon media-header__close"
                            onClick={onClose}
                            aria-label="Close player"
                        >
                            <ArrowLeftIcon
                                className="media-icon"
                                weight="bold"
                            />
                        </button>
                    )}
                    {title && (
                        <div className="media-header__info">
                            <span className="media-header__title">{title}</span>
                            {subtitle && (
                                <span className="media-header__subtitle">
                                    {subtitle}
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
                                <ErrorDialog.Close className="media-button media-button--primary">
                                    OK
                                </ErrorDialog.Close>
                            </div>
                        </div>
                    </ErrorDialog.Popup>
                </ErrorDialog.Root>

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
                            <TimeSlider.Root className="media-slider">
                                <TimeSlider.Track className="media-slider__track">
                                    <TimeSlider.Fill className="media-slider__fill" />
                                    <TimeSlider.Buffer className="media-slider__buffer" />
                                </TimeSlider.Track>
                                <TimeSlider.Thumb className="media-slider__thumb" />
                                <TimeSlider.Thumb className="react-time-slider-parts__thumb" />

                                <div className="media-surface media-preview media-slider__preview">
                                    <Slider.Thumbnail className="media-preview__thumbnail" />
                                    <TimeSlider.Value
                                        type="pointer"
                                        className="media-time media-preview__time"
                                    />
                                    <div className="media-preview__spinner media-icon">
                                        <Loader />
                                    </div>
                                </div>
                            </TimeSlider.Root>
                            <Time.Value
                                type="duration"
                                className="media-time"
                            />
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

                            <Tooltip.Root side="top">
                                <Tooltip.Trigger
                                    render={
                                        <CaptionsButton
                                            className="media-button--captions"
                                            render={<Button />}
                                        >
                                            <ClosedCaptioningIcon
                                                className="media-icon media-icon--captions-off"
                                                weight="regular"
                                            />
                                            <ClosedCaptioningIcon
                                                className="media-icon media-icon--captions-on"
                                                weight="fill"
                                            />
                                        </CaptionsButton>
                                    }
                                />
                                <Tooltip.Popup className="media-surface media-tooltip" />
                            </Tooltip.Root>

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

                <div className="media-overlay" />
            </Container>
        </Player.Provider>
    )
}

// ================================================================
// Components
// ================================================================

const Button = forwardRef<HTMLButtonElement, ComponentProps<'button'>>(
    function Button({ className, ...props }, ref) {
        return (
            <button
                ref={ref}
                type="button"
                className={`media-button media-button--subtle media-button--icon ${className ?? ''}`}
                {...props}
            />
        )
    },
)

function VolumePopover(): ReactNode {
    const volumeUnsupported = usePlayer(
        (s) => s.volumeAvailability === 'unsupported',
    )

    const muteButton = (
        <MuteButton className="media-button--mute" render={<Button />}>
            <SpeakerXIcon
                className="media-icon media-icon--volume-off"
                weight="fill"
            />
            <SpeakerLowIcon
                className="media-icon media-icon--volume-low"
                weight="fill"
            />
            <SpeakerHighIcon
                className="media-icon media-icon--volume-high"
                weight="fill"
            />
        </MuteButton>
    )

    if (volumeUnsupported) return muteButton

    return (
        <Popover.Root openOnHover delay={200} closeDelay={100} side="top">
            <Popover.Trigger render={muteButton} />
            <Popover.Popup className="media-surface media-popover media-popover--volume">
                <VolumeSlider.Root
                    className="media-slider"
                    orientation="vertical"
                    thumbAlignment="edge"
                >
                    <VolumeSlider.Track className="media-slider__track">
                        <VolumeSlider.Fill className="media-slider__fill" />
                    </VolumeSlider.Track>
                    <VolumeSlider.Thumb className="media-slider__thumb media-slider__thumb--persistent" />
                </VolumeSlider.Root>
            </Popover.Popup>
        </Popover.Root>
    )
}
