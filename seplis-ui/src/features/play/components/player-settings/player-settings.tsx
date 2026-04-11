import { useState, type ReactNode } from 'react'
import {
    BITRATE_OPTIONS,
    MAX_BITRATE,
} from '../../constants/play-bitrate.constants'
import { bitratePretty } from '../../utils/play-bitrate.utils'
import { AdvancedPanel } from './advanced-panel'
import { AudioPanel } from './audio-panel'
import { AudioTrackLabel } from './audio-track-label'
import { BitratePanel } from './bitrate-panel'
import { MainPanel, SettingsPanel } from './main-panel'
import { PlayerSettingsProps } from './player-settings.types'
import { SourcePanel } from './source-panel'
import { SubtitleSyncPanel } from './subtitle-sync-panel'
import { SubtitlesPanel } from './subtitles-panel'

import { trackLabel } from '../../utils/play-track.utils'
import classes from './player-settings.module.css'

interface Props extends PlayerSettingsProps {}

export function PlayerSettings({
    playRequestSource,
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
    onClose,
    playSettings,
}: Props): ReactNode {
    const [panel, setPanel] = useState<SettingsPanel>('main')
    const { source: currentSource, request: currentRequest } = playRequestSource

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
        if (!track) return audioLang
        return <AudioTrackLabel track={track} />
    })()

    const subtitleLabel = (() => {
        if (!activeSubtitleKey) return 'Off'
        const [lang, idxStr] = activeSubtitleKey.split(':')
        const sub = currentSource.subtitles.find(
            (s) => s.language === lang && s.index === parseInt(idxStr),
        )
        if (!sub) return lang
        return (
            <>
                {trackLabel(sub.title, sub.language)}
                {sub.forced && ' (Forced)'}
            </>
        )
    })()

    const back = () => setPanel('main')

    return (
        <div className={classes.settings}>
            {panel === 'main' && (
                <MainPanel
                    currentSource={currentSource}
                    playRequestsSources={playRequestsSources}
                    currentBitrateLabel={currentBitrateLabel}
                    currentAudioLabel={currentAudioLabel}
                    subtitleLabel={subtitleLabel}
                    subtitleOffset={subtitleOffset}
                    forceTranscode={forceTranscode}
                    onForceTranscodeChange={onForceTranscodeChange}
                    setPanel={setPanel}
                    hdrEnabled={playSettings.settings.hdrEnabled}
                    onHdrChange={(value) =>
                        playSettings.update({ hdrEnabled: value })
                    }
                />
            )}
            {panel === 'source' && (
                <SourcePanel
                    playRequestsSources={playRequestsSources}
                    currentRequest={currentRequest}
                    currentSource={currentSource}
                    onSourceChange={onSourceChange}
                    back={back}
                    onClose={onClose}
                />
            )}
            {panel === 'bitrate' && (
                <BitratePanel
                    availableBitrates={availableBitrates}
                    maxBitrate={maxBitrate}
                    currentSource={currentSource}
                    onBitrateChange={onBitrateChange}
                    back={back}
                    onClose={onClose}
                />
            )}
            {panel === 'audio' && (
                <AudioPanel
                    currentSource={currentSource}
                    audioLang={audioLang}
                    preferredAudioLangs={preferredAudioLangs}
                    onAudioLangChange={onAudioLangChange}
                    back={back}
                    onClose={onClose}
                />
            )}
            {panel === 'subtitles' && (
                <SubtitlesPanel
                    currentSource={currentSource}
                    activeSubtitleKey={activeSubtitleKey}
                    preferredSubtitleLangs={preferredSubtitleLangs}
                    onSubtitleChange={onSubtitleChange}
                    back={back}
                    onClose={onClose}
                />
            )}
            {panel === 'subtitle-sync' && (
                <SubtitleSyncPanel
                    subtitleOffset={subtitleOffset}
                    onSubtitleOffsetChange={onSubtitleOffsetChange}
                    back={back}
                />
            )}
            {panel === 'advanced' && (
                <AdvancedPanel playSettings={playSettings} back={back} />
            )}
        </div>
    )
}
