import { Anchor, Container, Flex, Image, Paper, Title } from '@mantine/core'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ResetPasswordForm } from './components/reset-password-form'

export function Component() {
    const { key } = useParams<{ key?: string }>()
    const navigate = useNavigate()

    if (!key) throw new Error('Missing key')

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
                <Title mb="2rem">Reset Password</Title>
                <Flex gap="1rem" direction="column">
                    <ResetPasswordForm
                        resetKey={key}
                        onSuccess={() => navigate('/login')}
                    />
                </Flex>
            </Paper>
        </Container>
    )
}
