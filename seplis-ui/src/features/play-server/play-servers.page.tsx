import { Container, Stack, Title } from '@mantine/core'
import { PlayServerList } from './components/play-server-list'

export function Component() {
    return (
        <Container size="lg" py="lg">
            <Stack gap="lg">
                <Title order={1}>Play servers</Title>
                <PlayServerList />
            </Stack>
        </Container>
    )
}
