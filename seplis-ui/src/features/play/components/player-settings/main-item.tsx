import { CaretRightIcon } from '@phosphor-icons/react'
import { type ReactNode } from 'react'
import classes from './player-settings.module.css'

interface Props {
    label: string
    value?: ReactNode
    onClick: () => void
    disabled?: boolean
}

export function MainItem({
    label,
    value,
    onClick,
    disabled,
}: Props): ReactNode {
    return (
        <div
            role="button"
            tabIndex={disabled ? -1 : 0}
            aria-disabled={disabled}
            className={classes.mainItem}
            onClick={disabled ? undefined : onClick}
            onKeyDown={
                disabled
                    ? undefined
                    : (e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault()
                              onClick()
                          }
                      }
            }
        >
            <span className={classes.mainLabel}>{label}</span>
            {value && <span className={classes.mainValue}>{value}</span>}
            {!disabled && (
                <CaretRightIcon className={classes.chevron} weight="bold" />
            )}
        </div>
    )
}
