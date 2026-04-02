import { ErrorBox } from '@/components/error-box'
import { Button, Flex, PasswordInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useResetPassword } from '../api/reset-password.api'
import { ResetPasswordCreate } from '../types/reset-password.types'

interface Props {
    resetKey: string
    onSuccess?: () => void
}

export function ResetPasswordForm({ resetKey, onSuccess }: Props) {
    const form = useForm<ResetPasswordCreate>({
        initialValues: {
            new_password: '',
            key: resetKey,
        },
    })
    const resetPassword = useResetPassword({
        onSuccess,
    })

    return (
        <form
            onSubmit={form.onSubmit((values) => {
                console.log(values)
                resetPassword.mutate({
                    data: values,
                })
            })}
        >
            <Flex gap="1rem" direction="column">
                <PasswordInput
                    placeholder="New password"
                    type="password"
                    autoFocus
                    required
                    w="100%"
                    size="lg"
                    key={form.key('new_password')}
                    {...form.getInputProps('new_password')}
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
                        Reset Password
                    </Button>
                </Flex>
            </Flex>
        </form>
    )
}
