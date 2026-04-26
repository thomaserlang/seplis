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
import { TranscodeDecisionPanel } from './transcode-decision-panel'

import { parseLangKey } from '../../utils/play-source.utils'
import { trackLabel } from '../../utils/play-track.utils'
import classes from './player-settings.module.css'

interface Props extends PlayerSettingsProps {}

export function PlayerSettings({
    playRequestSource,
    playRequestsSources,
    audioKey,
    forceTranscode,
    activeSubtitleKey,
    subtitleOffset,
    canAdjustSubtitleOffset,
    onSourceChange,
    onAudioLangChange,
    onForceTranscodeChange,
    onSubtitleKeyChange,
    onSubtitleOffsetChange,
    preferredAudioLangs,
    preferredSubtitleLangs,
    onClose,
    playSettings,
    transcodeDecision,
    playbackTransport,
}: Props): ReactNode {
    const [panel, setPanel] = useState<SettingsPanel>('main')
    const { source: currentSource, request: currentRequest } = playRequestSource

    const availableBitrates = BITRATE_OPTIONS.filter(
        (b) => b === MAX_BITRATE || b < currentSource.bitrate,
    )

    const currentBitrateLabel =
        playSettings.settings.maxBitrate === MAX_BITRATE
            ? `Max (${bitratePretty(currentSource.bitrate)})`
            : bitratePretty(playSettings.settings.maxBitrate)

    const currentAudioLabel = (() => {
        if (!audioKey) return 'Default'
        const [lang, idxStr] = audioKey.split(':')
        const index = parseInt(idxStr, 10)
        const track =
            currentSource.audio.find(
                (a) => a.language === lang && a.index === index,
            ) ?? currentSource.audio.find((a) => a.language === lang)
        if (!track) return audioKey
        return <AudioTrackLabel track={track} />
    })()

    const subtitleLabel = (() => {
        if (!activeSubtitleKey) return 'Off'
        const { lang, index } = parseLangKey(activeSubtitleKey)
        const sub = currentSource.subtitles.find(
            (s) => s.language === lang && s.group_index === index,
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
                    canAdjustSubtitleOffset={canAdjustSubtitleOffset}
                    forceTranscode={forceTranscode}
                    onForceTranscodeChange={onForceTranscodeChange}
                    transcodeDecision={transcodeDecision}
                    playbackTransport={playbackTransport}
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
                    maxBitrate={playSettings.settings.maxBitrate}
                    currentSource={currentSource}
                    onBitrateChange={(bitrate) => {
                        if (bitrate >= currentSource.bitrate) {
                            playSettings.update({ maxBitrate: undefined })
                        } else {
                            playSettings.update({ maxBitrate: bitrate })
                        }
                    }}
                    back={back}
                    onClose={onClose}
                />
            )}
            {panel === 'audio' && (
                <AudioPanel
                    currentSource={currentSource}
                    audioLang={audioKey}
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
                    onSubtitleChange={onSubtitleKeyChange}
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
            {panel === 'transcode-decision' && transcodeDecision && (
                <TranscodeDecisionPanel
                    transcodeDecision={transcodeDecision}
                    playbackTransport={playbackTransport}
                    back={back}
                />
            )}
            {panel === 'advanced' && (
                <AdvancedPanel playSettings={playSettings} back={back} />
            )}
        </div>
    )
}
