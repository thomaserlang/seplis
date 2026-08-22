import {
    Tooltip,
    AirPlayButton as VideoJsAirPlayButton,
    useMedia,
} from '@videojs/react'
import { AirPlayEnterIcon, AirPlayExitIcon } from '@videojs/react/icons'
import type { ReactNode } from 'react'
import { Button } from './button'

export function AirPlayButton(): ReactNode {
    const media = useMedia() as AirPlayMediaHost | null

    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <VideoJsAirPlayButton
                        className="media-button--airplay"
                        render={(props) => (
                            <Button
                                {...props}
                                onClick={(event) => {
                                    const video = media?.target
                                    if (video?.webkitShowPlaybackTargetPicker) {
                                        video.webkitShowPlaybackTargetPicker()
                                        return
                                    }
                                    props.onClick?.(event)
                                }}
                            />
                        )}
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

interface AirPlayMediaHost {
    target: AirPlayVideoElement | null
}

interface AirPlayVideoElement extends HTMLVideoElement {
    webkitShowPlaybackTargetPicker?: () => void
}
