import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

interface Props {
    label: string
    value: boolean
    onToggle: () => void
}

export function ToggleItem({ label, value, onToggle }: Props): ReactNode {
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
