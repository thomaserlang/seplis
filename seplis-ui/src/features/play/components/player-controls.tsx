import {
    AirplayIcon,
    SpeakerHighIcon,
    SpeakerLowIcon,
    SpeakerXIcon,
} from '@phosphor-icons/react'
import {
    MuteButton,
    Popover,
    Tooltip,
    VolumeSlider,
    useMedia,
    usePlayer,
} from '@videojs/react'
import { forwardRef, useEffect, useState, type ComponentProps, type ReactNode } from 'react'

export const Button = forwardRef<HTMLButtonElement, ComponentProps<'button'>>(
    function Button({ className, ...props }, ref) {
        return (
            <button
                ref={ref}
                type="button"
                className={`media-button media-button--subtle media-button--icon ${className ?? ''}`}
                {...props}
            />
        )
    },
)

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

export function AirPlayButton(): ReactNode {
    const media = useMedia()
    const [available, setAvailable] = useState(false)
    const [active, setActive] = useState(false)

    useEffect(() => {
        if (!media || !('webkitShowPlaybackTargetPicker' in media)) return

        const onAvailability = (e: Event) => {
            const availability = (e as any).availability
            setAvailable(availability === 'available')
        }
        const onConnectionChanged = () => {
            setActive(!!(media as any).webkitCurrentPlaybackTargetIsWireless)
        }

        media.addEventListener(
            'webkitplaybacktargetavailabilitychanged',
            onAvailability,
        )
        media.addEventListener(
            'webkitcurrentplaybacktargetiswirelesschanged',
            onConnectionChanged,
        )
        return () => {
            media.removeEventListener(
                'webkitplaybacktargetavailabilitychanged',
                onAvailability,
            )
            media.removeEventListener(
                'webkitcurrentplaybacktargetiswirelesschanged',
                onConnectionChanged,
            )
        }
    }, [media])

    if (!available) return null

    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <button
                        type="button"
                        aria-label="AirPlay"
                        className={`media-button media-button--subtle media-button--icon${active ? ' media-button--airplay-active' : ''}`}
                        onClick={() =>
                            (media as any)?.webkitShowPlaybackTargetPicker()
                        }
                    >
                        <AirplayIcon
                            className="media-icon"
                            weight={active ? 'fill' : 'regular'}
                        />
                    </button>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip">
                {active ? 'Disconnect AirPlay' : 'AirPlay'}
            </Tooltip.Popup>
        </Tooltip.Root>
    )
}
