import { Container, Stack, Title } from '@mantine/core'
import { Navigate } from 'react-router-dom'
import { useActiveUser } from './api/session.store'
import { UserStats } from './components/user-stats'

export function Component() {
    const [user] = useActiveUser()
    if (!user) return <Navigate to="/login" replace />

    return (
        <Container size="md" py="lg">
            <title>Stats</title>
            <Stack gap="lg">
                <Title order={1}>Stats</Title>
                <UserStats key={user.id} userId={user.id} />
            </Stack>
        </Container>
    )
}
