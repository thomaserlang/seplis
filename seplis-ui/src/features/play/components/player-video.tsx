import { PageLoader } from '@/components/page-loader'
import { Loader } from '@mantine/core'
import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    ArrowLeftIcon,
    CaretLeftIcon,
    CaretRightIcon,
    CheckIcon,
    ClosedCaptioningIcon,
    CornersInIcon,
    CornersOutIcon,
    GearIcon,
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
    selectTextTrack,
    useMedia,
    usePlayer,
    usePopoverContext,
} from '@videojs/react'
import { Video, videoFeatures } from '@videojs/react/video'
import {
    forwardRef,
    useCallback,
    useEffect,
    useState,
    type ComponentProps,
    type ReactNode,
} from 'react'
import {
    BITRATE_OPTIONS,
    MAX_BITRATE,
} from '../constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlayServerMedia,
} from '../types/play-source.types'
import {
    bitratePretty,
    playSourceBitrateStr,
} from '../utils/play-bitrate.utils'
import { playSourceStr } from '../utils/play-source.utils'

import './player-video.css'

const SEEK_TIME = 10

export const Player = createPlayer({ features: videoFeatures })

export interface VideoPlayerProps {
    currentPlayRequestSource: PlayRequestSource
    media: PlayServerMedia
    title?: string
    subtitle?: string
    onClose?: () => void
    playRequestsSources: PlayRequestSources[]
    maxBitrate: number
    audioLang: string | undefined
    onSourceChange: (source: PlayRequestSource) => void
    onBitrateChange: (bitrate: number) => void
    onAudioLangChange: (lang: string | undefined) => void
}

export function PlayerVideo({
    currentPlayRequestSource,
    media,
    title,
    subtitle,
    onClose,
    playRequestsSources,
    maxBitrate,
    audioLang,
    onSourceChange,
    onBitrateChange,
    onAudioLangChange,
}: VideoPlayerProps): ReactNode {
    return (
        <Container className={`media-default-skin media-default-skin--video`}>
            <Video src={media.hls_url} autoPlay />

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

                        <SettingsPopover
                            currentPlayRequestSource={currentPlayRequestSource}
                            playRequestsSources={playRequestsSources}
                            maxBitrate={maxBitrate}
                            audioLang={audioLang}
                            onSourceChange={onSourceChange}
                            onBitrateChange={onBitrateChange}
                            onAudioLangChange={onAudioLangChange}
                        />

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

function VideoClickHandler(): ReactNode {
    const media = useMedia()

    const togglePlayback = useCallback(() => {
        if (!media) return
        if (media.paused) {
            media.play()
        } else {
            media.pause()
        }
    }, [media])

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (
                e.code === 'Space' &&
                !(e.target instanceof HTMLInputElement) &&
                !(e.target instanceof HTMLTextAreaElement)
            ) {
                e.preventDefault()
                togglePlayback()
            }
        }
        document.addEventListener('keydown', handleKeyDown)
        return () => document.removeEventListener('keydown', handleKeyDown)
    }, [togglePlayback])

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

// ─── Settings ────────────────────────────────────────────────────────────────

type SettingsPanel = 'main' | 'source' | 'bitrate' | 'audio' | 'subtitles'

interface SettingsPopoverProps {
    currentPlayRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    maxBitrate: number
    audioLang: string | undefined
    onSourceChange: (source: PlayRequestSource) => void
    onBitrateChange: (bitrate: number) => void
    onAudioLangChange: (lang: string | undefined) => void
}

function SettingsPopover({
    currentPlayRequestSource,
    playRequestsSources,
    maxBitrate,
    audioLang,
    onSourceChange,
    onBitrateChange,
    onAudioLangChange,
}: SettingsPopoverProps): ReactNode {
    const [panel, setPanel] = useState<SettingsPanel>('main')
    const media = useMedia()
    const tracks = usePlayer(selectTextTrack)
    const { source: currentSource, request: currentRequest } =
        currentPlayRequestSource

    const [activeSubtitleKey, setActiveSubtitleKey] = useState<
        string | undefined
    >(undefined)

    const availableBitrates = BITRATE_OPTIONS.filter(
        (b) => b === MAX_BITRATE || b < currentSource.bit_rate,
    )

    const currentBitrateLabel =
        maxBitrate === MAX_BITRATE
            ? `Max (${bitratePretty(currentSource.bit_rate)})`
            : bitratePretty(maxBitrate)

    const currentAudioLabel = audioLang
        ? (currentSource.audio.find((a) => a.language === audioLang)?.title ??
          audioLang)
        : 'Default'

    const subtitleLabel = (() => {
        if (!activeSubtitleKey) return 'Off'
        const [lang, idxStr] = activeSubtitleKey.split(':')
        const sub = currentSource.subtitles.find(
            (s) => s.language === lang && s.index === parseInt(idxStr),
        )
        return sub?.title || lang
    })()

    console.log(tracks)
    const setSubtitle = (key: string | undefined) => {
        console.log(tracks)
        tracks?.toggleSubtitles(true)
        if (!media) return
        // Disable all subtitle/caption tracks first

        for (const track of Array.from(media.textTracks ?? [])) {
            if (track.kind === 'subtitles' || track.kind === 'captions') {
                track.mode = 'disabled'
            }
        }
        if (key) {
            const [lang, idxStr] = key.split(':')
            const srcIdx = parseInt(idxStr)
            // Find which position this subtitle is among same-language tracks
            const langGroup = currentSource.subtitles.filter(
                (s) => s.language === lang,
            )
            const posInGroup = langGroup.findIndex((s) => s.index === srcIdx)
            // Match to the nth text track with that language
            const matchingTracks = Array.from(media.textTracks ?? []).filter(
                (t) =>
                    (t.kind === 'subtitles' || t.kind === 'captions') &&
                    t.language === lang,
            )
            const target = matchingTracks[posInGroup] ?? matchingTracks[0]
            console.log(target)
            if (target) target.mode = 'showing'
        }
        setActiveSubtitleKey(key)
        back()
    }

    const gearButton = (
        <Button aria-label="Settings">
            <GearIcon className="media-icon" weight="bold" />
        </Button>
    )

    const back = () => setPanel('main')

    return (
        <Popover.Root side="top">
            <Popover.Trigger render={gearButton} />
            <Popover.Popup className="media-surface media-popover media-popover--settings">
                <div className="media-settings">
                    {panel === 'main' && (
                        <>
                            <MainItem
                                label="Source"
                                value={playSourceStr(currentSource)}
                                onClick={() => setPanel('source')}
                            />
                            <MainItem
                                label="Bitrate"
                                value={currentBitrateLabel}
                                onClick={() => setPanel('bitrate')}
                            />
                            {currentSource.audio.length > 1 && (
                                <MainItem
                                    label="Audio"
                                    value={currentAudioLabel}
                                    onClick={() => setPanel('audio')}
                                />
                            )}
                            {currentSource.subtitles.length > 0 && (
                                <MainItem
                                    label="Subtitles"
                                    value={subtitleLabel}
                                    onClick={() => setPanel('subtitles')}
                                />
                            )}
                        </>
                    )}

                    {panel === 'source' && (
                        <>
                            <SubMenuHeader title="Source" onBack={back} />
                            {playRequestsSources.map((server) =>
                                server.sources.map((src) => (
                                    <OptionItem
                                        key={`${server.request.play_id}-${src.index}`}
                                        active={
                                            currentRequest.play_id ===
                                                server.request.play_id &&
                                            currentSource.index === src.index
                                        }
                                        onClick={() => {
                                            onSourceChange({
                                                request: server.request,
                                                source: src,
                                            })
                                            back()
                                        }}
                                    >
                                        {playSourceStr(src)}
                                    </OptionItem>
                                )),
                            )}
                        </>
                    )}

                    {panel === 'bitrate' && (
                        <>
                            <SubMenuHeader title="Bitrate" onBack={back} />
                            {availableBitrates.map((bitrate) => (
                                <OptionItem
                                    key={bitrate}
                                    active={maxBitrate === bitrate}
                                    onClick={() => {
                                        onBitrateChange(bitrate)
                                        back()
                                    }}
                                >
                                    {bitrate === MAX_BITRATE
                                        ? `Max (${bitratePretty(currentSource.bit_rate)})`
                                        : playSourceBitrateStr(
                                              bitrate,
                                              currentSource,
                                          )}
                                </OptionItem>
                            ))}
                        </>
                    )}

                    {panel === 'audio' && (
                        <>
                            <SubMenuHeader title="Audio" onBack={back} />
                            {currentSource.audio.map((track) => (
                                <OptionItem
                                    key={track.index}
                                    active={audioLang === track.language}
                                    onClick={() => {
                                        onAudioLangChange(track.language)
                                        back()
                                    }}
                                >
                                    {track.title || track.language}
                                </OptionItem>
                            ))}
                        </>
                    )}

                    {panel === 'subtitles' && (
                        <>
                            <SubMenuHeader title="Subtitles" onBack={back} />
                            <OptionItem
                                active={!activeSubtitleKey}
                                onClick={() => setSubtitle(undefined)}
                            >
                                Off
                            </OptionItem>
                            {currentSource.subtitles.map((track) => {
                                const key = `${track.language}:${track.index}`
                                return (
                                    <OptionItem
                                        key={key}
                                        active={activeSubtitleKey === key}
                                        onClick={() => setSubtitle(key)}
                                    >
                                        {track.title || track.language}
                                        {track.forced && ' (Forced)'}
                                    </OptionItem>
                                )
                            })}
                        </>
                    )}
                </div>
            </Popover.Popup>
        </Popover.Root>
    )
}

function MainItem({
    label,
    value,
    onClick,
}: {
    label: string
    value?: string
    onClick: () => void
}): ReactNode {
    return (
        <button
            type="button"
            className="media-settings__main-item"
            onClick={onClick}
        >
            <span className="media-settings__main-label">{label}</span>
            {value && (
                <span className="media-settings__main-value">{value}</span>
            )}
            <CaretRightIcon className="media-settings__chevron" weight="bold" />
        </button>
    )
}

function SubMenuHeader({
    title,
    onBack,
}: {
    title: string
    onBack: () => void
}): ReactNode {
    return (
        <button
            type="button"
            className="media-settings__sub-header"
            onClick={onBack}
        >
            <CaretLeftIcon
                className="media-settings__back-icon"
                weight="bold"
            />
            <span className="media-settings__sub-title">{title}</span>
        </button>
    )
}

function OptionItem({
    active,
    onClick,
    children,
}: {
    active: boolean
    onClick: () => void
    children: ReactNode
}): ReactNode {
    const { popover } = usePopoverContext()
    return (
        <button
            type="button"
            className={`media-settings__option${active ? ' media-settings__option--active' : ''}`}
            onClick={() => {
                onClick()
                popover.close()
            }}
        >
            <span className="media-settings__option-check">
                {active && <CheckIcon weight="bold" />}
            </span>
            {children}
        </button>
    )
}
