import { useState, type ReactNode } from 'react'
import { OptionItem } from './option-item'
import classes from './player-settings.module.css'
import { SettingsBody } from './settings-body'
import { SubMenuHeader } from './sub-menu-header'

interface Props {
    title: string
    options: string[]
    selected: string[]
    defaultSelected: string[]
    onApply: (next: string[]) => void
    back: () => void
}

export function MultiSelectPanel({
    title,
    options,
    selected,
    defaultSelected,
    onApply,
    back,
}: Props): ReactNode {
    const [local, setLocal] = useState(selected)

    const toggle = (value: string) => {
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
                        key={option}
                        active={local.includes(option)}
                        onClick={() => toggle(option)}
                    >
                        {option}
                    </OptionItem>
                ))}
            </SettingsBody>
            <div className={classes.subActions}>
                <div
                    role="button"
                    tabIndex={0}
                    className={classes.subReset}
                    onClick={() => setLocal(defaultSelected)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault()
                            setLocal(defaultSelected)
                        }
                    }}
                >
                    Reset
                </div>
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
