import {
    CaretLeftIcon,
    CaretRightIcon,
    CheckIcon,
    GearIcon,
    MinusIcon,
    PlusIcon,
} from '@phosphor-icons/react'
import { Popover, usePlayer, usePopoverContext } from '@videojs/react'
import { useEffect, useState, type ReactNode } from 'react'
import { BITRATE_OPTIONS, MAX_BITRATE } from '../constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'
import {
    bitratePretty,
    playSourceBitrateStr,
} from '../utils/play-bitrate.utils'
import { audioCodecLabel, iso6392ToDisplayName, playSourceStr } from '../utils/play-source.utils'
import { Button } from './player-controls'

type SettingsPanel =
    | 'main'
    | 'source'
    | 'bitrate'
    | 'audio'
    | 'subtitles'
    | 'subtitle-sync'

const PANEL_TITLES: Partial<Record<SettingsPanel, string>> = {
    source: 'Source',
    bitrate: 'Bitrate',
    audio: 'Audio',
    subtitles: 'Subtitles',
    'subtitle-sync': 'Subtitle Sync',
}

export interface SettingsPopoverProps {
    currentPlayRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    maxBitrate: number
    audioLang: string | undefined
    forceTranscode: boolean
    activeSubtitleKey: string | undefined
    subtitleOffset: number
    onSourceChange: (source: PlayRequestSource) => void
    onBitrateChange: (bitrate: number) => void
    onAudioLangChange: (lang: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange: (key: string | undefined) => void
    onSubtitleOffsetChange: (offset: number) => void
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
}

export function SettingsPopover({
    currentPlayRequestSource,
    playRequestsSources,
    maxBitrate,
    audioLang,
    forceTranscode,
    activeSubtitleKey,
    subtitleOffset,
    onSourceChange,
    onBitrateChange,
    onAudioLangChange,
    onForceTranscodeChange,
    onSubtitleChange,
    onSubtitleOffsetChange,
    preferredAudioLangs,
    preferredSubtitleLangs,
}: SettingsPopoverProps): ReactNode {
    const [panel, setPanel] = useState<SettingsPanel>('main')
    const [open, setOpen] = useState(false)
    const controlsVisible = usePlayer((s) => s.controlsVisible)
    const { source: currentSource, request: currentRequest } =
        currentPlayRequestSource

    const availableBitrates = BITRATE_OPTIONS.filter(
        (b) => b === MAX_BITRATE || b < currentSource.bit_rate,
    )

    const currentBitrateLabel =
        maxBitrate === MAX_BITRATE
            ? `Max (${bitratePretty(currentSource.bit_rate)})`
            : bitratePretty(maxBitrate)

    const currentAudioLabel = (() => {
        if (!audioLang) return 'Default'
        const [lang, idxStr] = audioLang.split(':')
        const index = parseInt(idxStr, 10)
        const track =
            currentSource.audio.find(
                (a) => a.language === lang && a.index === index,
            ) ?? currentSource.audio.find((a) => a.language === lang)
        return track?.title ?? track?.language ?? audioLang
    })()

    const subtitleLabel = (() => {
        if (!activeSubtitleKey) return 'Off'
        const [lang, idxStr] = activeSubtitleKey.split(':')
        const sub = currentSource.subtitles.find(
            (s) => s.language === lang && s.index === parseInt(idxStr),
        )
        return sub?.title || lang
    })()

    const back = () => setPanel('main')

    const setSubtitle = (key: string | undefined) => {
        onSubtitleChange(key)
        back()
    }

    const gearButton = (
        <Button aria-label="Settings">
            <GearIcon className="media-icon" weight="bold" />
        </Button>
    )

    useEffect(() => {
        if (!controlsVisible && open) {
            setOpen(false)
        }
    }, [controlsVisible, open])

    return (
        <Popover.Root
            side="top"
            open={open}
            onOpenChange={(nextOpen) => {
                if (nextOpen) {
                    setPanel('main')
                }
                setOpen(nextOpen)
            }}
        >
            <Popover.Trigger render={gearButton} />
            <Popover.Popup className="media-surface media-popover media-popover--settings">
                {panel !== 'main' && (
                    <SubMenuHeader
                        title={PANEL_TITLES[panel] ?? ''}
                        onBack={back}
                    />
                )}
                <div className="media-settings" data-panel={panel}>
                    {panel === 'main' && (
                        <>
                            <MainItem
                                label="Source"
                                value={playSourceStr(currentSource)}
                                onClick={() => setPanel('source')}
                                disabled={
                                    playRequestsSources.reduce(
                                        (n, s) => n + s.sources.length,
                                        0,
                                    ) <= 1
                                }
                            />
                            <MainItem
                                label="Bitrate"
                                value={currentBitrateLabel}
                                onClick={() => setPanel('bitrate')}
                            />
                            <MainItem
                                label="Audio"
                                value={currentAudioLabel}
                                onClick={() => setPanel('audio')}
                                disabled={currentSource.audio.length <= 1}
                            />
                            <MainItem
                                label="Subtitles"
                                value={subtitleLabel}
                                onClick={() => setPanel('subtitles')}
                                disabled={currentSource.subtitles.length === 0}
                            />
                            <MainItem
                                label="Subtitle Sync"
                                value={
                                    subtitleOffset === 0
                                        ? '0s'
                                        : `${subtitleOffset > 0 ? '+' : ''}${subtitleOffset.toFixed(1)}s`
                                }
                                onClick={() => setPanel('subtitle-sync')}
                            />
                            <ToggleItem
                                label="Force Transcode"
                                value={forceTranscode}
                                onToggle={() =>
                                    onForceTranscodeChange(!forceTranscode)
                                }
                            />
                        </>
                    )}

                    {panel === 'source' &&
                        playRequestsSources.map((server) =>
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

                    {panel === 'bitrate' &&
                        availableBitrates.map((bitrate) => (
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

                    {panel === 'audio' &&
                        (() => {
                            const preferred = currentSource.audio.filter((t) =>
                                preferredAudioLangs?.includes(t.language),
                            )
                            const other = currentSource.audio.filter(
                                (t) =>
                                    !preferredAudioLangs?.includes(t.language),
                            )
                            const audioKey = (t: {
                                language: string
                                index: number
                            }) => `${t.language}:${t.index}`
                            return (
                                <>
                                    {preferred.map((track) => (
                                        <OptionItem
                                            key={track.index}
                                            active={
                                                audioLang === audioKey(track)
                                            }
                                            onClick={() => {
                                                onAudioLangChange(
                                                    audioKey(track),
                                                )
                                                back()
                                            }}
                                        >
                                            <AudioTrackLabel track={track} />
                                        </OptionItem>
                                    ))}
                                    {preferred.length > 0 &&
                                        other.length > 0 && (
                                            <SettingsGroupDivider />
                                        )}
                                    {other.map((track) => (
                                        <OptionItem
                                            key={track.index}
                                            active={
                                                audioLang === audioKey(track)
                                            }
                                            onClick={() => {
                                                onAudioLangChange(
                                                    audioKey(track),
                                                )
                                                back()
                                            }}
                                        >
                                            <AudioTrackLabel track={track} />
                                        </OptionItem>
                                    ))}
                                </>
                            )
                        })()}

                    {panel === 'subtitles' &&
                        (() => {
                            const preferred = currentSource.subtitles.filter(
                                (t) =>
                                    preferredSubtitleLangs?.includes(
                                        t.language,
                                    ),
                            )
                            const other = currentSource.subtitles.filter(
                                (t) =>
                                    !preferredSubtitleLangs?.includes(
                                        t.language,
                                    ),
                            )
                            return (
                                <>
                                    <OptionItem
                                        active={!activeSubtitleKey}
                                        onClick={() => setSubtitle(undefined)}
                                    >
                                        Off
                                    </OptionItem>
                                    {preferred.map((track) => {
                                        const key = `${track.language}:${track.index}`
                                        return (
                                            <OptionItem
                                                key={key}
                                                active={
                                                    activeSubtitleKey === key
                                                }
                                                onClick={() => setSubtitle(key)}
                                            >
                                                {trackLabel(
                                                    track.title,
                                                    track.language,
                                                )}
                                                {track.forced && ' (Forced)'}
                                            </OptionItem>
                                        )
                                    })}
                                    {preferred.length > 0 &&
                                        other.length > 0 && (
                                            <SettingsGroupDivider />
                                        )}
                                    {other.map((track) => {
                                        const key = `${track.language}:${track.index}`
                                        return (
                                            <OptionItem
                                                key={key}
                                                active={
                                                    activeSubtitleKey === key
                                                }
                                                onClick={() => setSubtitle(key)}
                                            >
                                                {trackLabel(
                                                    track.title,
                                                    track.language,
                                                )}
                                                {track.forced && ' (Forced)'}
                                            </OptionItem>
                                        )
                                    })}
                                </>
                            )
                        })()}

                    {panel === 'subtitle-sync' && (
                        <>
                            <div className="media-settings__sync">
                                <button
                                    type="button"
                                    className="media-settings__sync-btn"
                                    onClick={() =>
                                        onSubtitleOffsetChange(
                                            Math.round(
                                                (subtitleOffset - 0.5) * 10,
                                            ) / 10,
                                        )
                                    }
                                >
                                    <MinusIcon weight="bold" />
                                </button>
                                <span className="media-settings__sync-value">
                                    {subtitleOffset === 0
                                        ? '0s'
                                        : `${subtitleOffset > 0 ? '+' : ''}${subtitleOffset.toFixed(1)}s`}
                                </span>
                                <button
                                    type="button"
                                    className="media-settings__sync-btn"
                                    onClick={() =>
                                        onSubtitleOffsetChange(
                                            Math.round(
                                                (subtitleOffset + 0.5) * 10,
                                            ) / 10,
                                        )
                                    }
                                >
                                    <PlusIcon weight="bold" />
                                </button>
                            </div>
                            <button
                                type="button"
                                className="media-settings__sync-reset"
                                disabled={subtitleOffset === 0}
                                onClick={() => onSubtitleOffsetChange(0)}
                            >
                                Reset
                            </button>
                        </>
                    )}
                </div>
            </Popover.Popup>
        </Popover.Root>
    )
}

function ToggleItem({
    label,
    value,
    onToggle,
}: {
    label: string
    value: boolean
    onToggle: () => void
}): ReactNode {
    return (
        <button
            type="button"
            className="media-settings__main-item"
            onClick={onToggle}
        >
            <span className="media-settings__main-label">{label}</span>
            <span className="media-settings__main-value">
                {value ? 'On' : 'Off'}
            </span>
        </button>
    )
}

function MainItem({
    label,
    value,
    onClick,
    disabled,
}: {
    label: string
    value?: string
    onClick: () => void
    disabled?: boolean
}): ReactNode {
    return (
        <button
            type="button"
            className="media-settings__main-item"
            onClick={disabled ? undefined : onClick}
            disabled={disabled}
        >
            <span className="media-settings__main-label">{label}</span>
            {value && (
                <span className="media-settings__main-value">{value}</span>
            )}
            {!disabled && (
                <CaretRightIcon
                    className="media-settings__chevron"
                    weight="bold"
                />
            )}
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

function trackLabel(title: string | undefined, language: string): string {
    const base = title || language
    const displayName = iso6392ToDisplayName(language)
    if (!displayName) return base
    if (base.toLowerCase().includes(displayName.toLowerCase())) return base
    return `${base} (${displayName})`
}

function AudioTrackLabel({
    track,
}: {
    track: { title: string; language: string; codec: string | null }
}): ReactNode {
    const label = trackLabel(track.title, track.language)
    const codec = audioCodecLabel(track.codec, track.title)
    return (
        <span className="media-settings__audio-track">
            {label}
            {codec && (
                <span className="media-settings__audio-codec">{codec}</span>
            )}
        </span>
    )
}

function SettingsGroupDivider(): ReactNode {
    return <div className="media-settings__group-divider" />
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
