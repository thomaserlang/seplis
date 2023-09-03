import { FormControl, FormLabel, Stack, Switch } from '@chakra-ui/react'
import { useState } from 'react'
import { useController, Control } from 'react-hook-form'

export interface ISwitchRadioGroupOption {
    name: string
    value: string
}

export const SwitchRadioGroup = ({ control, name, options }: { control: Control<any, any>, name: string, options: ISwitchRadioGroupOption[] }) => {
    const { field } = useController({ control, name })

    const [value, setValue] = useState<string>(field.value || '')

    return <Stack spacing="0.25rem">
        {options && options.map(option => (
            <FormControl key={option.name} display='flex' alignItems='center' justifyContent='space-between'>
                <FormLabel htmlFor={`${name}-${option.name}-${option.value}`} flexGrow={1} mb='0' cursor='pointer'>
                    {option.name}
                </FormLabel>
                <Switch 
                    id={`${name}-${option.name}-${option.value}`} 
                    size='lg' 
                    value={option.value}
                    isChecked={value === option.value}
                    onChange={(e) => {
                        let v: string = ''
                        if (e.target.checked) {
                            v = option.value
                        }
                        setValue(v)
                        field.onChange(v)
                    }}
                />
            </FormControl>
        ))}
    </Stack>
}