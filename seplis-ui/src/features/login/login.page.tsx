import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Anchor, Container, Flex, Image, Paper, Title } from '@mantine/core'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useGetCurrentUser } from '../user/api/user.api'
import { LoginForm } from './components/login-form'
import { Token, UsersLoggedIn } from './types/login.types'

export function Component() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const currentUser = useGetCurrentUser({
        options: {
            enabled: false,
        },
    })

    const handleLogin = async (token: Token) => {
        localStorage.setItem('accessToken', token.access_token)
        const r = await currentUser.refetch()
        if (!r.data) return

        const users: UsersLoggedIn = JSON.parse(
            localStorage.getItem('users') || '{}',
        )
        users[r.data.id] = {
            ...r.data,
            token: token.access_token,
        }
        localStorage.setItem('users', JSON.stringify(users))
        localStorage.setItem('activeUser', JSON.stringify(r.data))

        const next = searchParams.get('next')
        if (next && next.startsWith('/')) {
            navigate(next)
        } else {
            navigate('/')
        }
    }

    return (
        <Container size="30rem" mt="2rem">
            <Flex justify="center" align="center" mb="2rem">
                <Anchor component={Link} to="/">
                    <Image
                        radius="50%"
                        w="4rem"
                        src="/img/android-chrome-96x96.png"
                    />
                </Anchor>
            </Flex>
            <Paper withBorder shadow="sm" p="2rem">
                <Title mb="2rem">Log in to SEPLIS</Title>
                <Flex gap="1rem" direction="column">
                    {currentUser.error && (
                        <ErrorBox errorObj={currentUser.error} />
                    )}
                    {currentUser.isLoading || currentUser.isRefetching ? (
                        <PageLoader />
                    ) : (
                        <LoginForm onSuccess={handleLogin} />
                    )}
                </Flex>
            </Paper>
        </Container>
    )
}
