import {
    CornersInIcon,
    CornersOutIcon,
    PictureInPictureIcon,
} from '@phosphor-icons/react'
import {
    FullscreenButton,
    PiPButton,
    PlaybackRateButton,
    Tooltip,
} from '@videojs/react'
import type { PlayerVideoControlsProps } from '../player-video.types'
import { AirPlayButton } from './airplay-button'
import { Button } from './button'
import { ChromecastButton } from './chromecast-button'
import { SettingsPopover } from './settings-popover'
import { VolumePopover } from './volume-popover'

type SecondaryControlsProps = Pick<
    PlayerVideoControlsProps,
    | 'playRequestSource'
    | 'playRequestsSources'
    | 'audio'
    | 'forceTranscode'
    | 'activeSubtitleKey'
    | 'subtitleOffset'
    | 'canAdjustSubtitleOffset'
    | 'onSourceChange'
    | 'onAudioChange'
    | 'onForceTranscodeChange'
    | 'onSubtitleChange'
    | 'onSubtitleOffsetChange'
    | 'preferredAudioLangs'
    | 'preferredSubtitleLangs'
    | 'playSettings'
>

export function PlayerSecondaryControls({
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
}: SecondaryControlsProps) {
    return (
        <div className="media-button-group" style={{ marginLeft: 'auto' }}>
            <Tooltip.Root side="top">
                <Tooltip.Trigger
                    render={
                        <PlaybackRateButton
                            className="media-button--playback-rate"
                            render={<Button />}
                        />
                    }
                />
                <Tooltip.Popup className="media-surface media-tooltip">
                    Toggle playback rate
                </Tooltip.Popup>
            </Tooltip.Root>

            <VolumePopover />

            <SettingsPopover
                playRequestSource={playRequestSource}
                playRequestsSources={playRequestsSources}
                audioKey={audio}
                forceTranscode={forceTranscode}
                activeSubtitleKey={activeSubtitleKey}
                subtitleOffset={subtitleOffset}
                canAdjustSubtitleOffset={canAdjustSubtitleOffset}
                onSourceChange={onSourceChange}
                onAudioLangChange={onAudioChange}
                onForceTranscodeChange={onForceTranscodeChange}
                onSubtitleKeyChange={onSubtitleChange}
                onSubtitleOffsetChange={onSubtitleOffsetChange}
                preferredAudioLangs={preferredAudioLangs}
                preferredSubtitleLangs={preferredSubtitleLangs}
                playSettings={playSettings}
            />

            <AirPlayButton />
            <ChromecastButton />
            <PictureInPictureToggle />
            <FullscreenToggle />
        </div>
    )
}

function PictureInPictureToggle() {
    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <PiPButton
                        className="media-button--pip"
                        render={<Button />}
                    >
                        <PictureInPictureIcon
                            className="media-icon media-icon--pip-enter"
                            weight="regular"
                        />
                        <PictureInPictureIcon
                            className="media-icon media-icon--pip-exit"
                            weight="fill"
                        />
                    </PiPButton>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip" />
        </Tooltip.Root>
    )
}

function FullscreenToggle() {
    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <FullscreenButton
                        className="media-button--fullscreen"
                        render={<Button />}
                    >
                        <CornersOutIcon
                            className="media-icon media-icon--fullscreen-enter"
                            weight="bold"
                        />
                        <CornersInIcon
                            className="media-icon media-icon--fullscreen-exit"
                            weight="bold"
                        />
                    </FullscreenButton>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip" />
        </Tooltip.Root>
    )
}
