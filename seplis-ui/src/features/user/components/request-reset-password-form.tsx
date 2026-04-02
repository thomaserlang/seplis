import { ErrorBox } from '@/components/error-box'
import { Alert, Button, Flex, Text, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useCreateRequestResetPassword } from '../api/reset-password.api'
import { RequestResetPasswordCreate } from '../types/reset-password.types'

interface Props {
    onSuccess?: () => void
}

export function RequestResetPasswordForm({ onSuccess }: Props) {
    const form = useForm<RequestResetPasswordCreate>({
        mode: 'uncontrolled',
        initialValues: {
            email: '',
        },
        onValuesChange: () => {
            resetPassword.reset()
        },
    })
    const resetPassword = useCreateRequestResetPassword({
        onSuccess,
    })

    if (resetPassword.isSuccess) {
        return (
            <Alert color="green">
                <Text span fw={600}>
                    If an account with that email exists, a reset link has been
                    sent.
                </Text>
            </Alert>
        )
    }

    return (
        <form
            onSubmit={form.onSubmit((values) => {
                resetPassword.mutate({
                    data: values,
                })
            })}
        >
            <Flex gap="1rem" direction="column">
                <TextInput
                    placeholder="Email"
                    type="email"
                    autoFocus
                    required
                    w="100%"
                    size="lg"
                    key={form.key('email')}
                    {...form.getInputProps('email')}
                />

                {resetPassword.error && (
                    <ErrorBox errorObj={resetPassword.error} />
                )}

                <Flex w="100%">
                    <Button
                        ml="auto"
                        size="lg"
                        type="submit"
                        loading={resetPassword.isPending}
                    >
                        Send Reset Link
                    </Button>
                </Flex>
            </Flex>
        </form>
    )
}
