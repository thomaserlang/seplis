import { CheckIcon } from '@phosphor-icons/react'
import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

interface Props {
    active: boolean
    onClick: () => void
    onClose?: () => void
    children: ReactNode
}

export function OptionItem({
    active,
    onClick,
    onClose,
    children,
}: Props): ReactNode {
    const handleSelect = () => {
        onClick()
        onClose?.()
    }
    return (
        <div
            role="button"
            tabIndex={0}
            className={`${classes.option}${active ? ` ${classes.optionActive}` : ''}`}
            onClick={handleSelect}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    handleSelect()
                }
            }}
        >
            <span className={classes.optionCheck}>
                {active && <CheckIcon weight="bold" />}
            </span>
            {children}
        </div>
    )
}
