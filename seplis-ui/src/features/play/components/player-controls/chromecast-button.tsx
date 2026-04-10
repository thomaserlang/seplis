import { useChromecast } from '@/features/play/components/chromecast/providers/chromecast-provider'
import { ScreencastIcon } from '@phosphor-icons/react'
import { Tooltip } from '@videojs/react'
import { type ReactNode } from 'react'

export function ChromecastButton(): ReactNode {
    const { isAvailable, isConnected, requestSession, endSession } =
        useChromecast()

    if (!isAvailable) return null

    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <button
                        type="button"
                        aria-label={
                            isConnected ? 'Disconnect Chromecast' : 'Cast to TV'
                        }
                        className="media-button media-button--subtle media-button--icon"
                        onClick={() =>
                            isConnected ? endSession() : requestSession()
                        }
                    >
                        <ScreencastIcon
                            className="media-icon"
                            weight={isConnected ? 'fill' : 'regular'}
                        />
                    </button>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip">
                {isConnected ? 'Disconnect Chromecast' : 'Cast to TV'}
            </Tooltip.Popup>
        </Tooltip.Root>
    )
}
