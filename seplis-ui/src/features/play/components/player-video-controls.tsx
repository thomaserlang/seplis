import { Controls, Tooltip } from '@videojs/react'
import {
    PlayerHeader,
    PlayerPrimaryControls,
    PlayerSecondaryControls,
    PlayerTimeControls,
    PlayerVideoInteractions as PlayerInteractions,
    PlayerVideoStatus as PlayerStatus,
} from './player-controls'
import type {
    PlayerVideoControlsProps,
    PlayerVideoStatusProps,
} from './player-video.types'

export function PlayerVideoStatus({
    ...props
}: PlayerVideoStatusProps) {
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
    isAirPlayActive,
    activeSubtitleKey,
    subtitleOffset,
    onSourceChange,
    onAudioChange,
    onForceTranscodeChange,
    onAirPlayActiveChange,
    onSubtitleChange,
    onSubtitleOffsetChange,
    preferredAudioLangs,
    preferredSubtitleLangs,
    playSettings,
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
                        isAirPlayActive={isAirPlayActive}
                        activeSubtitleKey={activeSubtitleKey}
                        subtitleOffset={subtitleOffset}
                        onSourceChange={onSourceChange}
                        onAudioChange={onAudioChange}
                        onForceTranscodeChange={onForceTranscodeChange}
                        onAirPlayActiveChange={onAirPlayActiveChange}
                        onSubtitleChange={onSubtitleChange}
                        onSubtitleOffsetChange={onSubtitleOffsetChange}
                        preferredAudioLangs={preferredAudioLangs}
                        preferredSubtitleLangs={preferredSubtitleLangs}
                        playSettings={playSettings}
                    />
                </Tooltip.Provider>
            </Controls.Root>
        </>
    )
}
