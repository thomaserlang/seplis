import { Controls, Tooltip } from '@videojs/react'
import {
    PlayerHeader,
    PlayerVideoInteractions as PlayerInteractions,
    PlayerPrimaryControls,
    PlayerSecondaryControls,
    PlayerVideoStatus as PlayerStatus,
    PlayerTimeControls,
} from './player-controls'
import type {
    PlayerVideoControlsProps,
    PlayerVideoStatusProps,
} from './player-video.types'

export function PlayerVideoStatus({ ...props }: PlayerVideoStatusProps) {
    return <PlayerStatus {...props} />
}

export function PlayerVideoInteractions() {
    return <PlayerInteractions />
}

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
    activeSubtitleKey,
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
            <PlayerHeader
                onClose={onClose}
                title={title}
                secondaryTitle={secondaryTitle}
            />

            <Controls.Root className="media-surface media-controls">
                <Tooltip.Provider>
                    <PlayerPrimaryControls onPlayNext={onPlayNext} />
                    <PlayerTimeControls timeSliderStyle={timeSliderStyle} />
                    <PlayerSecondaryControls
                        playRequestSource={playRequestSource}
                        playRequestsSources={playRequestsSources}
                        audio={audio}
                        forceTranscode={forceTranscode}
                        activeSubtitleKey={activeSubtitleKey}
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
        </>
    )
}
