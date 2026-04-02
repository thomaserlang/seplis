import { Logo } from '@/components/logo'
import { Container, Flex, Paper, Title } from '@mantine/core'
import { useNavigate, useParams } from 'react-router-dom'
import { ResetPasswordForm } from './components/reset-password-form'

export function Component() {
    const { key } = useParams<{ key?: string }>()
    const navigate = useNavigate()

    if (!key) throw new Error('Missing key')

    return (
        <Container size="30rem" mt="2rem">
            <Flex justify="center" align="center" mb="2rem">
                <Logo />
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
