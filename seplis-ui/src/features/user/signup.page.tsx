import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Container, Flex, Paper, Title } from '@mantine/core'
import { useNavigate } from 'react-router-dom'
import { useCreateToken } from './api/token.api'
import { LoginLogo } from './components/login-logo'
import { UserCreateForm } from './components/user-create-form'
import { User } from './types/user.types'
import { setLogin } from './utils/login.utils'

export function Component() {
    const navigate = useNavigate()
    const token = useCreateToken({})

    const handleSuccess = async ({
        user,
        password,
    }: {
        user: User
        password: string
    }) => {
        const r = await token.mutateAsync({
            data: {
                login: user.username,
                password: password,
                client_id: 'kN39jGJBpzujx5xzrCRd7p+oBuLkHzsCtOSaOR5K',
                grant_type: 'password',
            },
        })
        setLogin({
            user,
            token: r.access_token,
        })
        navigate('/')
    }

    return (
        <Container size="30rem" mt="2rem">
            <Flex justify="center" align="center" mb="2rem">
                <LoginLogo />
            </Flex>
            <Paper withBorder shadow="sm" p="2rem">
                <Title mb="2rem">Sign up to SEPLIS</Title>
                <Flex gap="1rem" direction="column">
                    {token.error && <ErrorBox errorObj={token.error} />}
                    {token.isPending ? (
                        <PageLoader />
                    ) : (
                        <UserCreateForm onSuccess={handleSuccess} />
                    )}
                </Flex>
            </Paper>
        </Container>
    )
}
