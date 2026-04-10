import { AirplayIcon } from '@phosphor-icons/react'
import { Tooltip, useMedia } from '@videojs/react'
import { useEffect, useState, type ReactNode } from 'react'

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
