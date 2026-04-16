import { ErrorBox } from '@/components/error-box'
import { Button, Flex, PasswordInput, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'

export interface PlayServerFormValues {
    name: string
    url: string
    secret: string
}

interface Props {
    initialValues: PlayServerFormValues
    submitLabel: string
    loading?: boolean
    error?: any
    secretRequired?: boolean
    onSubmit: (values: PlayServerFormValues) => void
    onCancel?: () => void
}

export function PlayServerForm({
    initialValues,
    submitLabel,
    loading,
    error,
    secretRequired = true,
    onSubmit,
    onCancel,
}: Props) {
    const form = useForm<PlayServerFormValues>({
        mode: 'uncontrolled',
        initialValues,
    })

    return (
        <form onSubmit={form.onSubmit(onSubmit)}>
            <Flex direction="column" gap="md">
                <TextInput
                    label="Name"
                    placeholder="Living room"
                    required
                    key={form.key('name')}
                    {...form.getInputProps('name')}
                />
                <TextInput
                    label="URL"
                    placeholder="https://play.example.com"
                    required
                    key={form.key('url')}
                    {...form.getInputProps('url')}
                />
                <PasswordInput
                    label="Secret"
                    placeholder="At least 20 characters"
                    required={secretRequired}
                    key={form.key('secret')}
                    {...form.getInputProps('secret')}
                />

                {error && error?.response?.status !== 422 && (
                    <ErrorBox errorObj={error} />
                )}

                <Flex justify="flex-end" gap="sm">
                    {onCancel && (
                        <Button
                            type="button"
                            variant="default"
                            onClick={onCancel}
                        >
                            Cancel
                        </Button>
                    )}
                    <Button type="submit" loading={loading}>
                        {submitLabel}
                    </Button>
                </Flex>
            </Flex>
        </form>
    )
}
