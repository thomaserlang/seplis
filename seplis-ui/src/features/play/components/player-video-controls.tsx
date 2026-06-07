import { Controls, Tooltip } from '@videojs/react'
import { useEffect, useRef } from 'react'
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
    const controlsRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const el = controlsRef.current
        if (!el) return
        const stop = (e: PointerEvent) => e.stopPropagation()
        el.addEventListener('pointerdown', stop)
        el.addEventListener('pointerup', stop)
        return () => {
            el.removeEventListener('pointerdown', stop)
            el.removeEventListener('pointerup', stop)
        }
    }, [])

    return (
        <>
            <PlayerHeader
                onClose={onClose}
                title={title}
                secondaryTitle={secondaryTitle}
            />

            <Controls.Root
                ref={controlsRef}
                className="media-surface media-controls"
            >
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
        </>
    )
}
