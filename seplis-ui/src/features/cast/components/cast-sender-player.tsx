import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    ArrowLeftIcon,
    CaretLeftIcon,
    CaretRightIcon,
    CheckIcon,
    GearIcon,
    MinusIcon,
    PauseIcon,
    PlayIcon,
    PlusIcon,
    ScreencastIcon,
} from '@phosphor-icons/react'
import { useEffect, useRef, useState, type ReactNode } from 'react'
import {
    BITRATE_OPTIONS,
    MAX_BITRATE,
} from '@/features/play/constants/play-bitrate.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '@/features/play/types/play-source.types'
import {
    bitratePretty,
    playSourceBitrateStr,
} from '@/features/play/utils/play-bitrate.utils'
import {
    iso6392ToDisplayName,
    playSourceStr,
} from '@/features/play/utils/play-source.utils'
import type { CastSenderAPI } from '../hooks/use-cast-sender'
import type { CastSenderMessage } from '../types/cast-messages.types'

import '@/features/play/components/player-video.css'

const SEEK_TIME = 10

interface CastSenderPlayerProps {
    cast: CastSenderAPI
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    playRequestsSources: PlayRequestSources[]
    currentPlayRequestSource: PlayRequestSource
    maxBitrate: number
    audio: string | undefined
    activeSubtitle: string | undefined
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    onSourceChange: (source: PlayRequestSource) => void
    onBitrateChange: (bitrate: number) => void
    onAudioChange: (audio: string | undefined) => void
    onSubtitleChange: (subtitle: string | undefined) => void
}

export function CastSenderPlayer({
    cast,
    title,
    secondaryTitle,
    onClose,
    playRequestsSources,
    currentPlayRequestSource,
    maxBitrate,
    audio,
    activeSubtitle,
    preferredAudioLangs,
    preferredSubtitleLangs,
    onSourceChange,
    onBitrateChange,
    onAudioChange,
    onSubtitleChange,
}: CastSenderPlayerProps): ReactNode {
    const { state, togglePlayPause, seek, sendMessage, stopCasting } = cast
    const [isDragging, setIsDragging] = useState(false)
    const [dragTime, setDragTime] = useState(0)
    const sliderRef = useRef<HTMLDivElement>(null)

    const displayTime = isDragging ? dragTime : state.currentTime
    const progress =
        state.duration > 0 ? (displayTime / state.duration) * 100 : 0

    const handleSliderClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!sliderRef.current || !state.duration) return
        const rect = sliderRef.current.getBoundingClientRect()
        const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
        seek(pct * state.duration)
    }

    const handleSliderMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!state.duration) return
        setIsDragging(true)
        updateDragFromEvent(e)

        const onMove = (ev: MouseEvent) => updateDragFromEvent(ev as any)
        const onUp = (ev: MouseEvent) => {
            setIsDragging(false)
            if (sliderRef.current && state.duration) {
                const rect = sliderRef.current.getBoundingClientRect()
                const pct = Math.max(
                    0,
                    Math.min(1, (ev.clientX - rect.left) / rect.width),
                )
                seek(pct * state.duration)
            }
            window.removeEventListener('mousemove', onMove)
            window.removeEventListener('mouseup', onUp)
        }
        window.addEventListener('mousemove', onMove)
        window.addEventListener('mouseup', onUp)
    }

    const updateDragFromEvent = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!sliderRef.current || !state.duration) return
        const rect = sliderRef.current.getBoundingClientRect()
        const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
        setDragTime(pct * state.duration)
    }

    const handleSendMessage = (msg: CastSenderMessage) => {
        sendMessage(msg)
        if (msg.type === 'setSubtitle') onSubtitleChange(msg.subtitle)
        if (msg.type === 'setAudio') onAudioChange(msg.audio)
        if (msg.type === 'setBitrate') onBitrateChange(msg.maxBitrate)
        if (msg.type === 'setSource') {
            const reqSrc = playRequestsSources.find(
                (s) => s.request.play_id === msg.playId,
            )
            const src = reqSrc?.sources.find((s) => s.index === msg.sourceIndex)
            if (reqSrc && src) onSourceChange({ request: reqSrc.request, source: src })
        }
    }

    return (
        <div
            className="media-default-skin media-default-skin--video"
            style={{
                position: 'fixed',
                inset: 0,
                background: '#111',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            {/* Header */}
            <div
                className="media-header"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.75rem 1rem',
                    flexShrink: 0,
                }}
            >
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
            </div>

            {/* Cast visual area */}
            <div
                style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.75rem',
                    color: '#aaa',
                }}
            >
                <ScreencastIcon size={64} weight="thin" style={{ opacity: 0.5 }} />
                {state.deviceName && (
                    <span style={{ fontSize: '0.9rem' }}>
                        Playing on <strong style={{ color: '#fff' }}>{state.deviceName}</strong>
                    </span>
                )}
            </div>

            {/* Controls */}
            <div
                className="media-surface media-controls"
                style={{ flexShrink: 0 }}
            >
                {/* Time slider */}
                <div className="media-time-controls">
                    <span className="media-time">{formatTime(displayTime)}</span>
                    <div
                        ref={sliderRef}
                        className="media-slider"
                        style={{ cursor: 'pointer' }}
                        onClick={handleSliderClick}
                        onMouseDown={handleSliderMouseDown}
                    >
                        <div className="media-slider__track">
                            <div
                                className="media-slider__fill"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                        <div
                            className="media-slider__thumb"
                            style={{ left: `${progress}%` }}
                        />
                    </div>
                    <span className="media-time">{formatTime(state.duration)}</span>
                </div>

                {/* Buttons row */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <div className="media-button-group">
                        {/* Play / Pause */}
                        <button
                            type="button"
                            className="media-button media-button--subtle media-button--icon media-button--play"
                            onClick={togglePlayPause}
                            aria-label={state.isPaused ? 'Play' : 'Pause'}
                        >
                            {state.isPaused ? (
                                <PlayIcon className="media-icon" weight="fill" />
                            ) : (
                                <PauseIcon className="media-icon" weight="fill" />
                            )}
                        </button>

                        {/* Seek backward */}
                        <button
                            type="button"
                            className="media-button media-button--subtle media-button--icon media-button--seek"
                            onClick={() => seek(Math.max(0, state.currentTime - SEEK_TIME))}
                            aria-label={`Seek backward ${SEEK_TIME}s`}
                        >
                            <ArrowCounterClockwiseIcon
                                className="media-icon media-icon--seek"
                                weight="bold"
                            />
                        </button>

                        {/* Seek forward */}
                        <button
                            type="button"
                            className="media-button media-button--subtle media-button--icon media-button--seek"
                            onClick={() => seek(state.currentTime + SEEK_TIME)}
                            aria-label={`Seek forward ${SEEK_TIME}s`}
                        >
                            <ArrowClockwiseIcon
                                className="media-icon media-icon--seek"
                                weight="bold"
                            />
                        </button>
                    </div>

                    <div
                        className="media-button-group"
                        style={{ marginLeft: 'auto' }}
                    >
                        <CastSettingsPopover
                            currentPlayRequestSource={currentPlayRequestSource}
                            playRequestsSources={playRequestsSources}
                            maxBitrate={maxBitrate}
                            audioLang={audio}
                            activeSubtitleKey={activeSubtitle}
                            preferredAudioLangs={preferredAudioLangs}
                            preferredSubtitleLangs={preferredSubtitleLangs}
                            onSendMessage={handleSendMessage}
                        />

                        {/* Stop casting */}
                        <button
                            type="button"
                            className="media-button media-button--subtle media-button--icon"
                            onClick={stopCasting}
                            aria-label="Stop casting"
                            title="Stop casting"
                        >
                            <ScreencastIcon className="media-icon" weight="fill" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

// ─── Settings popover (standalone, no Player.Provider needed) ─────────────────

type SettingsPanel = 'main' | 'source' | 'bitrate' | 'audio' | 'subtitles' | 'subtitle-sync'

interface CastSettingsPopoverProps {
    currentPlayRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    maxBitrate: number
    audioLang: string | undefined
    activeSubtitleKey: string | undefined
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    onSendMessage: (msg: CastSenderMessage) => void
}

function CastSettingsPopover({
    currentPlayRequestSource,
    playRequestsSources,
    maxBitrate,
    audioLang,
    activeSubtitleKey,
    preferredAudioLangs,
    preferredSubtitleLangs,
    onSendMessage,
}: CastSettingsPopoverProps): ReactNode {
    const [open, setOpen] = useState(false)
    const [panel, setPanel] = useState<SettingsPanel>('main')
    const [subtitleOffset, setSubtitleOffset] = useState(0)
    const popoverRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (!open) return
        const handler = (e: MouseEvent) => {
            if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
                setOpen(false)
            }
        }
        document.addEventListener('mousedown', handler)
        return () => document.removeEventListener('mousedown', handler)
    }, [open])

    const { source: currentSource, request: currentRequest } = currentPlayRequestSource

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
            currentSource.audio.find((a) => a.language === lang && a.index === index) ??
            currentSource.audio.find((a) => a.language === lang)
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
    const close = () => {
        setOpen(false)
        setPanel('main')
    }

    return (
        <div style={{ position: 'relative' }} ref={popoverRef}>
            <button
                type="button"
                className="media-button media-button--subtle media-button--icon"
                aria-label="Settings"
                onClick={() => {
                    setPanel('main')
                    setOpen((v) => !v)
                }}
            >
                <GearIcon className="media-icon" weight="bold" />
            </button>

            {open && (
                <div
                    className="media-surface media-popover media-popover--settings"
                    style={{
                        position: 'absolute',
                        bottom: '3rem',
                        right: 0,
                        zIndex: 100,
                        minWidth: '220px',
                    }}
                >
                    {panel !== 'main' && (
                        <button
                            type="button"
                            className="media-settings__sub-header"
                            onClick={back}
                        >
                            <CaretLeftIcon
                                className="media-settings__back-icon"
                                weight="bold"
                            />
                            <span className="media-settings__sub-title">
                                {panel === 'source'
                                    ? 'Source'
                                    : panel === 'bitrate'
                                      ? 'Bitrate'
                                      : panel === 'audio'
                                        ? 'Audio'
                                        : panel === 'subtitles'
                                          ? 'Subtitles'
                                          : 'Subtitle Sync'}
                            </span>
                        </button>
                    )}

                    <div className="media-settings" data-panel={panel}>
                        {panel === 'main' && (
                            <>
                                <CastSettingItem
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
                                <CastSettingItem
                                    label="Bitrate"
                                    value={currentBitrateLabel}
                                    onClick={() => setPanel('bitrate')}
                                />
                                <CastSettingItem
                                    label="Audio"
                                    value={currentAudioLabel}
                                    onClick={() => setPanel('audio')}
                                    disabled={currentSource.audio.length <= 1}
                                />
                                <CastSettingItem
                                    label="Subtitles"
                                    value={subtitleLabel}
                                    onClick={() => setPanel('subtitles')}
                                    disabled={currentSource.subtitles.length === 0}
                                />
                                <CastSettingItem
                                    label="Subtitle Sync"
                                    value={
                                        subtitleOffset === 0
                                            ? '0s'
                                            : `${subtitleOffset > 0 ? '+' : ''}${subtitleOffset.toFixed(1)}s`
                                    }
                                    onClick={() => setPanel('subtitle-sync')}
                                />
                            </>
                        )}

                        {panel === 'source' &&
                            playRequestsSources.map((server) =>
                                server.sources.map((src) => (
                                    <CastOptionItem
                                        key={`${server.request.play_id}-${src.index}`}
                                        active={
                                            currentRequest.play_id ===
                                                server.request.play_id &&
                                            currentSource.index === src.index
                                        }
                                        onClick={() => {
                                            onSendMessage({
                                                type: 'setSource',
                                                playId: server.request.play_id,
                                                sourceIndex: src.index,
                                            })
                                            close()
                                        }}
                                    >
                                        {playSourceStr(src)}
                                    </CastOptionItem>
                                )),
                            )}

                        {panel === 'bitrate' &&
                            availableBitrates.map((bitrate) => (
                                <CastOptionItem
                                    key={bitrate}
                                    active={maxBitrate === bitrate}
                                    onClick={() => {
                                        onSendMessage({
                                            type: 'setBitrate',
                                            maxBitrate: bitrate,
                                        })
                                        close()
                                    }}
                                >
                                    {bitrate === MAX_BITRATE
                                        ? `Max (${bitratePretty(currentSource.bit_rate)})`
                                        : playSourceBitrateStr(bitrate, currentSource)}
                                </CastOptionItem>
                            ))}

                        {panel === 'audio' &&
                            (() => {
                                const audioKey = (t: {
                                    language: string
                                    index: number
                                }) => `${t.language}:${t.index}`
                                const preferred = currentSource.audio.filter((t) =>
                                    preferredAudioLangs?.includes(t.language),
                                )
                                const other = currentSource.audio.filter(
                                    (t) => !preferredAudioLangs?.includes(t.language),
                                )
                                return (
                                    <>
                                        {preferred.map((track) => (
                                            <CastOptionItem
                                                key={track.index}
                                                active={audioLang === audioKey(track)}
                                                onClick={() => {
                                                    onSendMessage({
                                                        type: 'setAudio',
                                                        audio: audioKey(track),
                                                    })
                                                    close()
                                                }}
                                            >
                                                {trackLabel(track.title, track.language)}
                                            </CastOptionItem>
                                        ))}
                                        {preferred.length > 0 && other.length > 0 && (
                                            <div className="media-settings__group-divider" />
                                        )}
                                        {other.map((track) => (
                                            <CastOptionItem
                                                key={track.index}
                                                active={audioLang === audioKey(track)}
                                                onClick={() => {
                                                    onSendMessage({
                                                        type: 'setAudio',
                                                        audio: audioKey(track),
                                                    })
                                                    close()
                                                }}
                                            >
                                                {trackLabel(track.title, track.language)}
                                            </CastOptionItem>
                                        ))}
                                    </>
                                )
                            })()}

                        {panel === 'subtitles' &&
                            (() => {
                                const preferred = currentSource.subtitles.filter((t) =>
                                    preferredSubtitleLangs?.includes(t.language),
                                )
                                const other = currentSource.subtitles.filter(
                                    (t) => !preferredSubtitleLangs?.includes(t.language),
                                )
                                return (
                                    <>
                                        <CastOptionItem
                                            active={!activeSubtitleKey}
                                            onClick={() => {
                                                onSendMessage({
                                                    type: 'setSubtitle',
                                                    subtitle: undefined,
                                                })
                                                close()
                                            }}
                                        >
                                            Off
                                        </CastOptionItem>
                                        {preferred.map((track) => {
                                            const key = `${track.language}:${track.index}`
                                            return (
                                                <CastOptionItem
                                                    key={key}
                                                    active={activeSubtitleKey === key}
                                                    onClick={() => {
                                                        onSendMessage({
                                                            type: 'setSubtitle',
                                                            subtitle: key,
                                                        })
                                                        close()
                                                    }}
                                                >
                                                    {trackLabel(
                                                        track.title,
                                                        track.language,
                                                    )}
                                                    {track.forced && ' (Forced)'}
                                                </CastOptionItem>
                                            )
                                        })}
                                        {preferred.length > 0 && other.length > 0 && (
                                            <div className="media-settings__group-divider" />
                                        )}
                                        {other.map((track) => {
                                            const key = `${track.language}:${track.index}`
                                            return (
                                                <CastOptionItem
                                                    key={key}
                                                    active={activeSubtitleKey === key}
                                                    onClick={() => {
                                                        onSendMessage({
                                                            type: 'setSubtitle',
                                                            subtitle: key,
                                                        })
                                                        close()
                                                    }}
                                                >
                                                    {trackLabel(
                                                        track.title,
                                                        track.language,
                                                    )}
                                                    {track.forced && ' (Forced)'}
                                                </CastOptionItem>
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
                                            setSubtitleOffset(
                                                Math.round((subtitleOffset - 0.5) * 10) / 10,
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
                                            setSubtitleOffset(
                                                Math.round((subtitleOffset + 0.5) * 10) / 10,
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
                                    onClick={() => setSubtitleOffset(0)}
                                >
                                    Reset
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

function CastSettingItem({
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
            {value && <span className="media-settings__main-value">{value}</span>}
            {!disabled && (
                <CaretRightIcon className="media-settings__chevron" weight="bold" />
            )}
        </button>
    )
}

function CastOptionItem({
    active,
    onClick,
    children,
}: {
    active: boolean
    onClick: () => void
    children: ReactNode
}): ReactNode {
    return (
        <button
            type="button"
            className={`media-settings__option${active ? ' media-settings__option--active' : ''}`}
            onClick={onClick}
        >
            <span className="media-settings__option-check">
                {active && <CheckIcon weight="bold" />}
            </span>
            {children}
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

function formatTime(seconds: number): string {
    if (!isFinite(seconds) || seconds < 0) return '0:00'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    return `${m}:${String(s).padStart(2, '0')}`
}
