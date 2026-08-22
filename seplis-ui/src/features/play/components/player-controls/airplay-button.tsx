import { Tooltip, AirPlayButton as VideoJsAirPlayButton } from '@videojs/react'
import { AirPlayEnterIcon, AirPlayExitIcon } from '@videojs/react/icons'
import type { ReactNode } from 'react'
import { Button } from './button'

export function AirPlayButton(): ReactNode {
    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <VideoJsAirPlayButton
                        className="media-button--airplay"
                        render={<Button />}
                    >
                        <AirPlayEnterIcon className="media-icon media-icon--airplay-enter" />
                        <AirPlayExitIcon className="media-icon media-icon--airplay-exit" />
                    </VideoJsAirPlayButton>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip">
                <Tooltip.Label />
            </Tooltip.Popup>
        </Tooltip.Root>
    )
}
