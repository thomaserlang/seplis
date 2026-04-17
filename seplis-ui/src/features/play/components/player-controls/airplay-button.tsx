import { AirplayIcon } from '@phosphor-icons/react'
import type { Video as VideoMedia } from '@videojs/core'
import { Tooltip, useMedia } from '@videojs/react'
import { useEffect, useState, type ReactNode } from 'react'

type AirPlayAvailability = 'available' | 'not-available'

interface WebKitAvailabilityEvent extends Event {
    availability?: AirPlayAvailability
}

interface AirPlayMedia extends VideoMedia {
    webkitCurrentPlaybackTargetIsWireless?: boolean
    webkitShowPlaybackTargetPicker: () => void
    addEventListener(
        type: 'webkitplaybacktargetavailabilitychanged',
        listener: (event: WebKitAvailabilityEvent) => void,
        options?: boolean | AddEventListenerOptions,
    ): void
    addEventListener(
        type: 'webkitcurrentplaybacktargetiswirelesschanged',
        listener: EventListener,
        options?: boolean | AddEventListenerOptions,
    ): void
    removeEventListener(
        type: 'webkitplaybacktargetavailabilitychanged',
        listener: (event: WebKitAvailabilityEvent) => void,
        options?: boolean | EventListenerOptions,
    ): void
    removeEventListener(
        type: 'webkitcurrentplaybacktargetiswirelesschanged',
        listener: EventListener,
        options?: boolean | EventListenerOptions,
    ): void
}

export function AirPlayButton(): ReactNode {
    const media = useMedia() as VideoMedia | null
    const [available, setAvailable] = useState(false)
    const [active, setActive] = useState(false)

    useEffect(() => {
        if (!media || !('webkitShowPlaybackTargetPicker' in media)) return

        const airplayMedia = media as AirPlayMedia

        const onAvailability = (event: WebKitAvailabilityEvent) => {
            setAvailable(event.availability === 'available')
        }
        const onConnectionChanged = () => {
            setActive(!!airplayMedia.webkitCurrentPlaybackTargetIsWireless)
        }

        airplayMedia.addEventListener(
            'webkitplaybacktargetavailabilitychanged',
            onAvailability,
        )
        airplayMedia.addEventListener(
            'webkitcurrentplaybacktargetiswirelesschanged',
            onConnectionChanged,
        )
        return () => {
            airplayMedia.removeEventListener(
                'webkitplaybacktargetavailabilitychanged',
                onAvailability,
            )
            airplayMedia.removeEventListener(
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
                            (
                                media as AirPlayMedia | null
                            )?.webkitShowPlaybackTargetPicker()
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
