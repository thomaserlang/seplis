import { useState, type ReactNode } from 'react'
import { OptionItem } from './option-item'
import classes from './player-settings.module.css'
import { SettingsBody } from './settings-body'
import { SubMenuHeader } from './sub-menu-header'

interface Props<T extends string> {
    title: string
    options: { value: T; label: string }[]
    selected: T[]
    onApply: (next: T[] | undefined) => void
    back: () => void
}

export function MultiSelectPanel<T extends string>({
    title,
    options,
    selected,
    onApply,
    back,
}: Props<T>): ReactNode {
    const [local, setLocal] = useState(selected)

    const toggle = (value: T) => {
        setLocal((prev) => {
            if (prev.includes(value)) {
                return prev.length === 1
                    ? prev
                    : prev.filter((c) => c !== value)
            }
            return [...prev, value]
        })
    }

    return (
        <>
            <SubMenuHeader title={title} onBack={back} />
            <SettingsBody>
                {options.map((option) => (
                    <OptionItem
                        key={option.value}
                        active={local.includes(option.value)}
                        onClick={() => toggle(option.value)}
                    >
                        {option.label}
                    </OptionItem>
                ))}
            </SettingsBody>
            <div className={classes.subActions}>
                <div
                    role="button"
                    tabIndex={0}
                    className={classes.subApply}
                    onClick={() => {
                        onApply(local)
                        back()
                    }}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault()
                            onApply(local)
                            back()
                        }
                    }}
                >
                    Apply
                </div>
            </div>
        </>
    )
}
