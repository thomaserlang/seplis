import { Controls, Tooltip } from '@videojs/react'
import {
    PlayerHeader,
    PlayerPrimaryControls,
    PlayerSecondaryControls,
    PlayerTimeControls,
} from './player-controls'
import type { PlayerVideoControlsProps } from './player-video.types'

export function PlayerVideoControls({
    onClose,
    title,
    secondaryTitle,
    onPlayNext,
    timeSliderStyle,
    playRequestSource,
    playRequestsSources,
    audio,
    forceTranscode,
    subtitle,
    subtitleOffset,
    canAdjustSubtitleOffset,
    onSourceChange,
    onAudioChange,
    onForceTranscodeChange,
    onSubtitleChange,
    onSubtitleOffsetChange,
    preferredAudioLangs,
    preferredSubtitleLangs,
    playSettings,
    transcodeDecision,
    playbackTransport,
}: PlayerVideoControlsProps) {
    return (
        <>
            <Controls.Root className="media-surface media-controls">
                <Tooltip.Provider>
                    <PlayerPrimaryControls onPlayNext={onPlayNext} />
                    <PlayerTimeControls timeSliderStyle={timeSliderStyle} />
                    <PlayerSecondaryControls
                        playRequestSource={playRequestSource}
                        playRequestsSources={playRequestsSources}
                        audio={audio}
                        forceTranscode={forceTranscode}
                        subtitle={subtitle}
                        subtitleOffset={subtitleOffset}
                        canAdjustSubtitleOffset={canAdjustSubtitleOffset}
                        onSourceChange={onSourceChange}
                        onAudioChange={onAudioChange}
                        onForceTranscodeChange={onForceTranscodeChange}
                        onSubtitleChange={onSubtitleChange}
                        onSubtitleOffsetChange={onSubtitleOffsetChange}
                        preferredAudioLangs={preferredAudioLangs}
                        preferredSubtitleLangs={preferredSubtitleLangs}
                        playSettings={playSettings}
                        transcodeDecision={transcodeDecision}
                        playbackTransport={playbackTransport}
                    />
                </Tooltip.Provider>
            </Controls.Root>

            <PlayerHeader
                onClose={onClose}
                title={title}
                secondaryTitle={secondaryTitle}
            />
        </>
    )
}
