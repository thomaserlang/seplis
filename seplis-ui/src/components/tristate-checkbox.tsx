import { Checkbox, CheckboxProps } from '@mantine/core'

export function TristateCheckbox({
    onCheckedChanged,
    ...props
}: CheckboxProps & {
    onCheckedChanged?: (checked: boolean | undefined) => void
}) {
    return (
        <Checkbox
            indeterminate={props.checked === false}
            {...props}
            checked={!!props.checked}
            onChange={(e) => {
                const checked = e.currentTarget.checked
                if (props.checked === false) {
                    onCheckedChanged?.(undefined)
                } else {
                    onCheckedChanged?.(checked)
                }
                props.onChange?.(e)
            }}
        />
    )
}
