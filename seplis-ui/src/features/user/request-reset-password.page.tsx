import { Container, Flex, Paper, Title } from '@mantine/core'
import { LoginLogo } from './components/login-logo'
import { RequestResetPasswordForm } from './components/request-reset-password-form'

export function Component() {
    return (
        <Container size="30rem" mt="2rem">
            <Flex justify="center" align="center" mb="2rem">
                <LoginLogo />
            </Flex>
            <Paper withBorder shadow="sm" p="2rem">
                <Title mb="2rem">Password Reset</Title>
                <Flex gap="1rem" direction="column">
                    <RequestResetPasswordForm />
                </Flex>
            </Paper>
        </Container>
    )
}
