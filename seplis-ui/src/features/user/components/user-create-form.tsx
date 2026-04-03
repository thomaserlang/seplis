import { ErrorBox } from '@/components/error-box'
import { setFormErrors } from '@/utils/form.utils'
import { Button, Flex, PasswordInput, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useCreateUser } from '../api/user.api'
import { User, UserCreate } from '../types/user.types'

interface Props {
    onSuccess?: (props: { user: User; password: string }) => void
}

export function UserCreateForm({ onSuccess }: Props) {
    const form = useForm<UserCreate>({
        initialValues: {
            username: '',
            password: '',
            email: '',
        },
    })
    const create = useCreateUser({
        onSuccess: (data) => {
            onSuccess?.({ user: data, password: form.values.password })
        },
        onError: (error) => {
            if (error.response.status === 422) {
                setFormErrors(form, error)
            }
        },
    })

    return (
        <form
            onSubmit={form.onSubmit((values) => {
                create.mutate({
                    data: values,
                })
            })}
        >
            <Flex gap="1rem" direction="column">
                <TextInput
                    placeholder="Username"
                    autoFocus
                    required
                    w="100%"
                    size="lg"
                    key={form.key('username')}
                    {...form.getInputProps('username')}
                />
                <TextInput
                    placeholder="Email"
                    type="email"
                    required
                    w="100%"
                    size="lg"
                    key={form.key('email')}
                    {...form.getInputProps('email')}
                />
                <PasswordInput
                    placeholder="Password"
                    type="password"
                    required
                    w="100%"
                    size="lg"
                    key={form.key('password')}
                    {...form.getInputProps('password')}
                />

                {create.error && create.error?.response.status !== 422 && (
                    <ErrorBox errorObj={create.error} />
                )}

                <Flex w="100%">
                    <Button
                        ml="auto"
                        size="compact-lg"
                        type="submit"
                        loading={create.isPending}
                    >
                        Sign up
                    </Button>
                </Flex>
            </Flex>
        </form>
    )
}
