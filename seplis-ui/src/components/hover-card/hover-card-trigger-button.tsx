import { InfoIcon } from '@phosphor-icons/react'
import classes from './hover-card-trigger-button.module.css'

interface Props {
    onPointerEnter?: (e: React.PointerEvent<HTMLButtonElement>) => void
}

export function HoverCardTriggerButton({ onPointerEnter }: Props) {
    return (
        <button
            className={classes.trigger}
            onPointerEnter={onPointerEnter}
            onClick={(e) => e.stopPropagation()}
            aria-label="More info"
        >
            <InfoIcon size={14} weight="bold" />
        </button>
    )
}
