import { CaretLeftIcon } from '@phosphor-icons/react'
import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

interface Props {
    title: string
    onBack: () => void
}

export function SubMenuHeader({ title, onBack }: Props): ReactNode {
    return (
        <div
            role="button"
            tabIndex={0}
            className={classes.subHeader}
            onClick={onBack}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    onBack()
                }
            }}
        >
            <CaretLeftIcon className={classes.backIcon} weight="bold" />
            <span className={classes.subTitle}>{title}</span>
        </div>
    )
}
