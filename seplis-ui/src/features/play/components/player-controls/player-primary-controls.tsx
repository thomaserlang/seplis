import {
    ArrowClockwiseIcon,
    ArrowCounterClockwiseIcon,
    PauseIcon,
    PlayIcon,
    SkipForwardIcon,
} from '@phosphor-icons/react'
import { PlayButton, SeekButton, Tooltip } from '@videojs/react'
import { ComponentProps, ReactNode } from 'react'
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
                        <RestartIcon className="media-icon media-icon--restart" />

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

function RestartIcon(props: ComponentProps<'svg'>): ReactNode {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="none"
            aria-hidden="true"
            viewBox="0 0 18 18"
            {...props}
        >
            <path
                fill="currentColor"
                d="M9 17a8 8 0 0 1-8-8h2a6 6 0 1 0 1.287-3.713l1.286 1.286A.25.25 0 0 1 5.396 7H1.25A.25.25 0 0 1 1 6.75V2.604a.25.25 0 0 1 .427-.177l1.438 1.438A8 8 0 1 1 9 17"
            />
            <path
                fill="currentColor"
                d="m11.61 9.639-3.331 2.07a.826.826 0 0 1-1.15-.266.86.86 0 0 1-.129-.452V6.849C7 6.38 7.374 6 7.834 6c.158 0 .312.045.445.13l3.331 2.071a.858.858 0 0 1 0 1.438"
            />
        </svg>
    )
}
