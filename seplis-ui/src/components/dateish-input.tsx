import { Flex, Select } from '@mantine/core'
import { useForm } from '@mantine/form'

interface Props {
    defaultValue: string
    onChange: (value: string | undefined) => void
    label?: string
}

export function DateishInput({ defaultValue, onChange, label }: Props) {
    const currentYear = new Date().getFullYear() - 1900 + 1
    const year = defaultValue ? Number(defaultValue.substring(0, 4)) : undefined
    const month =
        defaultValue && defaultValue.length >= 7
            ? Number(defaultValue.substring(5, 7))
            : undefined
    const day =
        defaultValue && defaultValue.length >= 10
            ? Number(defaultValue.substring(8, 10))
            : undefined

    const form = useForm({
        mode: 'uncontrolled',
        initialValues: {
            year,
            month,
            day,
        },
        onValuesChange: (values) => {
            const { year, month, day } = values
            if (year) {
                onChange(
                    `${year}-${month ? String(month).padStart(2, '0') : '01'}-${
                        day ? String(day).padStart(2, '0') : '01'
                    }`,
                )
                return
            }
            onChange(undefined)
        },
    })

    return (
        <Flex gap="0.15rem" align="center">
            <Select
                w={120}
                placeholder="YYYY"
                data={Array.from({ length: currentYear }, (_, i) => {
                    const y = 1900 + i
                    return { value: y, label: String(y) }
                }).reverse()}
                label={label}
                key={form.key('year')}
                clearable
                {...form.getInputProps('year')}
            />
            <Select
                w={100}
                placeholder="MM"
                data={Array.from({ length: 12 }, (_, i) => {
                    const m = i + 1
                    return { value: m, label: String(m).padStart(2, '0') }
                })}
                key={form.key('month')}
                clearable
                {...form.getInputProps('month')}
            />
            <Select
                w={100}
                placeholder="DD"
                data={Array.from({ length: 31 }, (_, i) => {
                    const d = i + 1
                    return { value: d, label: String(d).padStart(2, '0') }
                })}
                key={form.key('day')}
                clearable
                {...form.getInputProps('day')}
            />
        </Flex>
    )
}
