import { ErrorBox } from '@/components/error-box'
import { Anchor, Button, Flex, PasswordInput, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { Link } from 'react-router-dom'
import { useCreateToken } from '../api/token.api'
import { Token, TokenCreate } from '../types/login.types'

interface Props {
    onSuccess: (token: Token) => void
}

export function LoginForm({ onSuccess }: Props) {
    const form = useForm<TokenCreate>({
        mode: 'uncontrolled',
        initialValues: {
            login: '',
            password: '',
            client_id: 'kN39jGJBpzujx5xzrCRd7p+oBuLkHzsCtOSaOR5K',
            grant_type: 'password',
        },
        onValuesChange: () => {
            token.reset()
        },
    })
    const token = useCreateToken({
        onSuccess: (data) => {
            onSuccess(data)
        },
    })

    return (
        <form
            onSubmit={form.onSubmit((values) => {
                token.mutate({
                    data: values,
                })
            })}
        >
            <Flex gap="1rem" direction="column">
                <TextInput
                    placeholder="Email or username"
                    autoFocus
                    required
                    w="100%"
                    size="lg"
                    key={form.key('login')}
                    {...form.getInputProps('login')}
                />
                <PasswordInput
                    placeholder="Password"
                    required
                    w="100%"
                    size="lg"
                    key={form.key('password')}
                    {...form.getInputProps('password')}
                />

                {token.error && <ErrorBox errorObj={token.error} />}

                <Flex w="100%" justify="space-between" align="center">
                    <Anchor
                        component={Link}
                        to="/request-reset-password"
                        c="var(--muted-foreground)"
                    >
                        Forgot password?
                    </Anchor>
                    <Button
                        ml="auto"
                        size="lg"
                        type="submit"
                        loading={token.isPending}
                    >
                        Login
                    </Button>
                </Flex>
            </Flex>
        </form>
    )
}
