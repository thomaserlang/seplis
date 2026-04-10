import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

export function ToggleItem({
    label,
    value,
    onToggle,
}: {
    label: string
    value: boolean
    onToggle: () => void
}): ReactNode {
    return (
        <div
            role="button"
            tabIndex={0}
            className={classes.mainItem}
            onClick={onToggle}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    onToggle()
                }
            }}
        >
            <span className={classes.mainLabel}>{label}</span>
            <span className={classes.mainValue}>{value ? 'On' : 'Off'}</span>
        </div>
    )
}
