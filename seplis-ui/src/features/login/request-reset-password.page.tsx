import { Anchor, Container, Flex, Image, Paper, Title } from '@mantine/core'
import { Link } from 'react-router-dom'
import { RequestResetPasswordForm } from './components/request-reset-password-form'

export function Component() {
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
                <Title mb="2rem">Password Reset</Title>
                <Flex gap="1rem" direction="column">
                    <RequestResetPasswordForm />
                </Flex>
            </Paper>
        </Container>
    )
}
