import {
    SpeakerHighIcon,
    SpeakerLowIcon,
    SpeakerXIcon,
} from '@phosphor-icons/react'
import {
    MuteButton,
    Popover,
    VolumeSlider,
    usePlayer,
} from '@videojs/react'
import { type ReactNode } from 'react'
import { Button } from './button'

export function VolumePopover(): ReactNode {
    const volumeUnsupported = usePlayer(
        (s) => s.volumeAvailability === 'unsupported',
    )

    const muteButton = (
        <MuteButton className="media-button--mute" render={<Button />}>
            <SpeakerXIcon
                className="media-icon media-icon--volume-off"
                weight="fill"
            />
            <SpeakerLowIcon
                className="media-icon media-icon--volume-low"
                weight="fill"
            />
            <SpeakerHighIcon
                className="media-icon media-icon--volume-high"
                weight="fill"
            />
        </MuteButton>
    )

    if (volumeUnsupported) return muteButton

    return (
        <Popover.Root openOnHover delay={200} closeDelay={100} side="top">
            <Popover.Trigger render={muteButton} />
            <Popover.Popup className="media-surface media-popover media-popover--volume">
                <VolumeSlider.Root
                    className="media-slider"
                    orientation="vertical"
                    thumbAlignment="edge"
                >
                    <VolumeSlider.Track className="media-slider__track">
                        <VolumeSlider.Fill className="media-slider__fill" />
                    </VolumeSlider.Track>
                    <VolumeSlider.Thumb className="media-slider__thumb media-slider__thumb--persistent" />
                </VolumeSlider.Root>
            </Popover.Popup>
        </Popover.Root>
    )
}
