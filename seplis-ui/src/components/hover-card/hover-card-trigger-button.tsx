import { InfoIcon } from '@phosphor-icons/react'
import classes from './hover-card-trigger-button.module.css'

interface Props {
    onMouseEnter?: (e: React.MouseEvent<HTMLButtonElement>) => void
}

export function HoverCardTriggerButton({ onMouseEnter }: Props) {
    return (
        <button
            className={classes.trigger}
            onMouseEnter={onMouseEnter}
            onClick={(e) => e.stopPropagation()}
            aria-label="More info"
        >
            <InfoIcon size={14} weight="bold" />
        </button>
    )
}
