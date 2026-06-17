import { useChromecast } from '@/features/play/components/chromecast/providers/chromecast-provider'
import { CircleNotchIcon, ScreencastIcon } from '@phosphor-icons/react'
import { Tooltip } from '@videojs/react'
import { type ReactNode } from 'react'

export function ChromecastButton(): ReactNode {
    const {
        isAvailable,
        isConnected,
        isConnecting,
        requestSession,
        endSession,
    } = useChromecast()

    if (!isAvailable) return null

    const label = isConnecting
        ? 'Connecting to Chromecast'
        : isConnected
          ? 'Disconnect Chromecast'
          : 'Cast to TV'

    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <button
                        type="button"
                        aria-label={label}
                        className="media-button media-button--subtle media-button--icon"
                        disabled={isConnecting}
                        onClick={() =>
                            isConnected ? endSession() : requestSession()
                        }
                    >
                        {isConnecting ? (
                            <CircleNotchIcon className="media-icon media-icon--spinner" />
                        ) : (
                            <ScreencastIcon
                                className="media-icon"
                                weight={isConnected ? 'fill' : 'regular'}
                            />
                        )}
                    </button>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip">
                {label}
            </Tooltip.Popup>
        </Tooltip.Root>
    )
}
