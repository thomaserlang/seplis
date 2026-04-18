import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    PauseIcon,
    PlayIcon,
    SkipForwardIcon,
} from '@phosphor-icons/react'
import { PlayButton, SeekButton, Tooltip } from '@videojs/react'
import { Button } from './button'

const SEEK_TIME = 10

export function PlayerPrimaryControls({
    onPlayNext,
}: {
    onPlayNext?: () => void
}) {
    return (
        <div className="media-button-group">
            <PlayToggleButton />
            <SeekControlButton seconds={-SEEK_TIME} direction="backward" />
            <SeekControlButton seconds={SEEK_TIME} direction="forward" />

            {onPlayNext && (
                <Tooltip.Root side="top">
                    <Tooltip.Trigger
                        render={
                            <Button
                                className="media-button--seek"
                                onClick={onPlayNext}
                                aria-label="Play next episode"
                            >
                                <SkipForwardIcon
                                    className="media-icon media-icon--seek"
                                    weight="fill"
                                />
                            </Button>
                        }
                    />
                    <Tooltip.Popup className="media-surface media-tooltip">
                        Play next episode
                    </Tooltip.Popup>
                </Tooltip.Root>
            )}
        </div>
    )
}

function PlayToggleButton() {
    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <PlayButton
                        className="media-button--play"
                        render={<Button />}
                    >
                        <ArrowCounterClockwiseIcon
                            className="media-icon media-icon--restart"
                            weight="bold"
                        />
                        <PlayIcon
                            className="media-icon media-icon--play"
                            weight="fill"
                        />
                        <PauseIcon
                            className="media-icon media-icon--pause"
                            weight="fill"
                        />
                    </PlayButton>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip" />
        </Tooltip.Root>
    )
}

function SeekControlButton({
    seconds,
    direction,
}: {
    seconds: number
    direction: 'backward' | 'forward'
}) {
    const icon =
        direction === 'backward' ? (
            <ArrowCounterClockwiseIcon
                className="media-icon media-icon--seek"
                weight="bold"
            />
        ) : (
            <ArrowClockwiseIcon
                className="media-icon media-icon--seek"
                weight="bold"
            />
        )
    const label =
        direction === 'backward'
            ? `Seek backward ${Math.abs(seconds)} seconds`
            : `Seek forward ${Math.abs(seconds)} seconds`

    return (
        <Tooltip.Root side="top">
            <Tooltip.Trigger
                render={
                    <SeekButton
                        seconds={seconds}
                        className="media-button--seek"
                        render={<Button />}
                    >
                        {icon}
                    </SeekButton>
                }
            />
            <Tooltip.Popup className="media-surface media-tooltip">
                {label}
            </Tooltip.Popup>
        </Tooltip.Root>
    )
}
