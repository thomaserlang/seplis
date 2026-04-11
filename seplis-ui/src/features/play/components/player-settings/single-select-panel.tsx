import { type ReactNode } from 'react'
import { OptionItem } from './option-item'
import { SettingsBody } from './settings-body'
import { SubMenuHeader } from './sub-menu-header'

export function SingleSelectPanel<T extends string | number>({
    title,
    options,
    value,
    onSelect,
    back,
    renderOption,
}: {
    title: string
    options: readonly T[]
    value: T
    onSelect: (v: T) => void
    back: () => void
    renderOption?: (v: T) => ReactNode
}): ReactNode {
    return (
        <>
            <SubMenuHeader title={title} onBack={back} />
            <SettingsBody>
                {options.map((option) => (
                    <OptionItem
                        key={String(option)}
                        active={value === option}
                        onClick={() => {
                            onSelect(option)
                            back()
                        }}
                    >
                        {renderOption ? renderOption(option) : String(option)}
                    </OptionItem>
                ))}
            </SettingsBody>
        </>
    )
}
