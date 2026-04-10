import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

export function SettingsGroupDivider(): ReactNode {
    return <div className={classes.groupDivider} />
}
