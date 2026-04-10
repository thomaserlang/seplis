import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

interface Props {
    children: ReactNode
    mah?: string
}

export function SettingsBody({ children, mah = '10rem' }: Props): ReactNode {
    return (
        <div className={classes.settingsBody} style={{ maxHeight: mah }}>
            {children}
        </div>
    )
}
