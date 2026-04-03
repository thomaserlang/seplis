import { ErrorBox } from '@/components/error-box'
import { Logo } from '@/components/logo'
import { PageLoader } from '@/components/page-loader'
import { Button, Container, Flex, Paper, Title } from '@mantine/core'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { setActiveUser } from './api/active-user.api'
import { useGetCurrentUser } from './api/user.api'
import { LoginForm } from './components/login-form'
import { Token } from './types/login.types'

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

        setActiveUser({
            user: r.data,
            token: token.access_token,
        })

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
                <Logo />
            </Flex>
            <Paper withBorder shadow="sm" p="2rem">
                <Title mb="2rem" mt="-0.5rem">
                    Log in to SEPLIS
                </Title>
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
            <Flex w="100%" justify="center">
                <Button
                    component={Link}
                    variant="subtle"
                    to="/signup"
                    mt="0.5rem"
                    size="compact-lg"
                >
                    Sign up
                </Button>
            </Flex>
        </Container>
    )
}
