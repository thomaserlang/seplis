import { type ReactNode } from 'react'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../../types/play-source.types'
import { playSourceStr } from '../../utils/play-source.utils'
import { MainItem } from './main-item'
import { SettingsBody } from './settings-body'
import { ToggleItem } from './toggle-item'

export type SettingsPanel =
    | 'main'
    | 'source'
    | 'bitrate'
    | 'audio'
    | 'subtitles'
    | 'subtitle-sync'
    | 'advanced'

interface Props {
    currentSource: PlayRequestSource['source']
    playRequestsSources: PlayRequestSources[]
    currentBitrateLabel: ReactNode
    currentAudioLabel: ReactNode
    subtitleLabel: ReactNode
    subtitleOffset: number
    canAdjustSubtitleOffset: boolean
    forceTranscode: boolean
    onForceTranscodeChange: (value: boolean) => void
    hdrEnabled: boolean
    onHdrChange: (value: boolean) => void
    setPanel: (panel: SettingsPanel) => void
}

export function MainPanel({
    currentSource,
    playRequestsSources,
    currentBitrateLabel,
    currentAudioLabel,
    subtitleLabel,
    subtitleOffset,
    canAdjustSubtitleOffset,
    forceTranscode,
    onForceTranscodeChange,
    setPanel,
    hdrEnabled,
    onHdrChange,
}: Props): ReactNode {
    return (
        <SettingsBody mah="">
            <MainItem label="Advanced" onClick={() => setPanel('advanced')} />
            <ToggleItem
                label="HDR"
                value={hdrEnabled}
                onToggle={() => {
                    onHdrChange(!hdrEnabled)
                }}
            />
            <ToggleItem
                label="Force Transcode"
                value={forceTranscode}
                onToggle={() => onForceTranscodeChange(!forceTranscode)}
            />
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
                label="Quality"
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
                    !canAdjustSubtitleOffset
                        ? 'Unavailable'
                        : subtitleOffset === 0
                          ? '0s'
                          : `${subtitleOffset > 0 ? '+' : ''}${subtitleOffset.toFixed(1)}s`
                }
                onClick={() => setPanel('subtitle-sync')}
                disabled={!canAdjustSubtitleOffset}
            />
        </SettingsBody>
    )
}
