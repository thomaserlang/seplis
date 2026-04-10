import { type ReactNode } from 'react'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../../types/play-source.types'
import { playSourceStr } from '../../utils/play-source.utils'
import { MainItem } from './main-item'
import { SettingsBody } from './settings-body'
import { type SettingsPanel } from './settings-panel.types'
import { ToggleItem } from './toggle-item'

export function MainPanel({
    currentSource,
    playRequestsSources,
    currentBitrateLabel,
    currentAudioLabel,
    subtitleLabel,
    subtitleOffset,
    forceTranscode,
    onForceTranscodeChange,
    setPanel,
}: {
    currentSource: PlayRequestSource['source']
    playRequestsSources: PlayRequestSources[]
    currentBitrateLabel: ReactNode
    currentAudioLabel: ReactNode
    subtitleLabel: ReactNode
    subtitleOffset: number
    forceTranscode: boolean
    onForceTranscodeChange: (value: boolean) => void
    setPanel: (panel: SettingsPanel) => void
}): ReactNode {
    return (
        <SettingsBody mah="">
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
                    subtitleOffset === 0
                        ? '0s'
                        : `${subtitleOffset > 0 ? '+' : ''}${subtitleOffset.toFixed(1)}s`
                }
                onClick={() => setPanel('subtitle-sync')}
            />
            <ToggleItem
                label="Force Transcode"
                value={forceTranscode}
                onToggle={() => onForceTranscodeChange(!forceTranscode)}
            />
        </SettingsBody>
    )
}
