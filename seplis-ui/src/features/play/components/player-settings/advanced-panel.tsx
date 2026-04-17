import { useState, type ReactNode } from 'react'
import { ALL_AUDIO_CHANNELS } from '../../constants/play-audio.constants'
import {
    UsePlaySettings,
    type PlaySettingsOverrides,
} from '../../hooks/use-play-settings'
import { channelLabel } from '../../utils/play-audio.utils'

import {
    AUDIO_CODEC_LABELS,
    AUDIO_CODECS,
    HDR_FORMAT_LABELS,
    HDR_FORMATS,
    STREAM_FORMATS,
    VIDEO_CODEC_LABELS,
    VIDEO_CODECS,
    VIDEO_CONTAINERS,
} from '../../types/media.types'
import { MainItem } from './main-item'
import { MultiSelectPanel } from './multi-select-panel'
import classes from './player-settings.module.css'
import { SettingsBody } from './settings-body'
import { SettingsGroupDivider } from './settings-group-divider'
import { SingleSelectPanel } from './single-select-panel'
import { SubMenuHeader } from './sub-menu-header'

type SubPanel =
    | 'main'
    | 'video-codecs'
    | 'transcode-video'
    | 'audio-codecs'
    | 'transcode-audio'
    | 'channels'
    | 'containers'
    | 'format'
    | 'hdr-formats'

interface Props {
    playSettings: UsePlaySettings
    back: () => void
}

export function AdvancedPanel({ playSettings, back }: Props): ReactNode {
    const [subPanel, setSubPanel] = useState<SubPanel>('main')

    const toMain = () => setSubPanel('main')
    const { settings } = playSettings

    if (subPanel === 'video-codecs') {
        return (
            <MultiSelectPanel
                title="Video Codecs"
                options={VIDEO_CODECS.map((c) => ({
                    value: c,
                    label: VIDEO_CODEC_LABELS[c],
                }))}
                selected={playSettings.settings.supportedVideoCodecs}
                onApply={(next) => {
                    const changes: Partial<PlaySettingsOverrides> = {
                        supportedVideoCodecs: next,
                    }
                    if (next && !next.includes(settings.transcodeVideoCodec)) {
                        changes.transcodeVideoCodec = next[0]
                    }
                    playSettings.update(changes)
                }}
                back={toMain}
            />
        )
    }

    if (subPanel === 'hdr-formats') {
        return (
            <MultiSelectPanel
                title="HDR Formats"
                options={HDR_FORMATS.map((f) => ({
                    value: f,
                    label: HDR_FORMAT_LABELS[f],
                }))}
                selected={settings.supportedHdrFormats}
                onApply={(next) =>
                    playSettings.update({ supportedHdrFormats: next })
                }
                back={toMain}
            />
        )
    }

    if (subPanel === 'transcode-video') {
        return (
            <SingleSelectPanel
                title="Transcode Video Codec"
                options={settings.supportedVideoCodecs}
                value={settings.transcodeVideoCodec}
                onSelect={(v) =>
                    playSettings.update({ transcodeVideoCodec: v })
                }
                back={toMain}
                renderOption={(v) => VIDEO_CODEC_LABELS[v]}
            />
        )
    }

    if (subPanel === 'audio-codecs') {
        return (
            <MultiSelectPanel
                title="Audio Codecs"
                options={AUDIO_CODECS.map((c) => ({
                    value: c,
                    label: AUDIO_CODEC_LABELS[c],
                }))}
                selected={settings.supportedAudioCodecs}
                onApply={(next) => {
                    const changes: Partial<PlaySettingsOverrides> = {
                        supportedAudioCodecs: next,
                    }
                    if (next && !next.includes(settings.transcodeAudioCodec)) {
                        changes.transcodeAudioCodec = next[0]
                    }
                    playSettings.update(changes)
                }}
                back={toMain}
            />
        )
    }

    if (subPanel === 'transcode-audio') {
        return (
            <SingleSelectPanel
                title="Transcode Audio Codec"
                options={AUDIO_CODECS}
                value={settings.transcodeAudioCodec}
                onSelect={(v) =>
                    playSettings.update({ transcodeAudioCodec: v })
                }
                back={toMain}
                renderOption={(v) => AUDIO_CODEC_LABELS[v]}
            />
        )
    }

    if (subPanel === 'channels') {
        return (
            <SingleSelectPanel
                title="Max Audio Channels"
                options={ALL_AUDIO_CHANNELS}
                value={settings.maxAudioChannels}
                onSelect={(v) => playSettings.update({ maxAudioChannels: v })}
                back={toMain}
                renderOption={channelLabel}
            />
        )
    }

    if (subPanel === 'containers') {
        return (
            <MultiSelectPanel
                title="Video Containers"
                options={VIDEO_CONTAINERS.map((c) => ({
                    value: c,
                    label: c,
                }))}
                selected={settings.supportedVideoContainers}
                onApply={(next) =>
                    playSettings.update({ supportedVideoContainers: next })
                }
                back={toMain}
            />
        )
    }

    if (subPanel === 'format') {
        return (
            <SingleSelectPanel
                title="Stream Format"
                options={STREAM_FORMATS}
                value={settings.format}
                onSelect={(v) => playSettings.update({ format: v })}
                back={toMain}
            />
        )
    }

    return (
        <>
            <SubMenuHeader title="Advanced" onBack={back} />
            <SettingsBody mah="">
                <MainItem
                    label="Transcode Video Codec"
                    value={VIDEO_CODEC_LABELS[settings.transcodeVideoCodec]}
                    onClick={() => setSubPanel('transcode-video')}
                />
                <MainItem
                    label="Video Codecs"
                    value={settings.supportedVideoCodecs
                        .map((c) => VIDEO_CODEC_LABELS[c])
                        .join(', ')}
                    onClick={() => setSubPanel('video-codecs')}
                />
                <MainItem
                    label="HDR Formats"
                    value={settings.supportedHdrFormats
                        ?.map((f) => HDR_FORMAT_LABELS[f])
                        .join(', ')}
                    onClick={() => setSubPanel('hdr-formats')}
                />
                <MainItem
                    label="Video Containers"
                    value={settings.supportedVideoContainers.join(', ')}
                    onClick={() => setSubPanel('containers')}
                />
                <MainItem
                    label="Audio Codecs"
                    value={settings.supportedAudioCodecs
                        .map((c) => AUDIO_CODEC_LABELS[c])
                        .join(', ')}
                    onClick={() => setSubPanel('audio-codecs')}
                />
                <MainItem
                    label="Transcode Audio Codec"
                    value={AUDIO_CODEC_LABELS[settings.transcodeAudioCodec]}
                    onClick={() => setSubPanel('transcode-audio')}
                />
                <MainItem
                    label="Max Audio Channels"
                    value={channelLabel(settings.maxAudioChannels)}
                    onClick={() => setSubPanel('channels')}
                />
                <MainItem
                    label="Stream Format"
                    value={settings.format}
                    onClick={() => setSubPanel('format')}
                />
                <SettingsGroupDivider />
                <div
                    role="button"
                    tabIndex={playSettings.isDefault ? -1 : 0}
                    aria-disabled={playSettings.isDefault}
                    className={classes.syncReset}
                    onClick={
                        playSettings.isDefault ? undefined : playSettings.reset
                    }
                    onKeyDown={
                        playSettings.isDefault
                            ? undefined
                            : (e) => {
                                  if (e.key === 'Enter' || e.key === ' ') {
                                      e.preventDefault()
                                      playSettings.reset()
                                  }
                              }
                    }
                >
                    Reset to defaults
                </div>
            </SettingsBody>
        </>
    )
}
