import { Container } from '@mantine/core'
import { Navigate, useParams } from 'react-router-dom'
import { PlayServerDetail } from './components/play-server-detail'

export function Component() {
    const { playServerId } = useParams()

    if (!playServerId) return <Navigate to="/play-servers" replace />

    return (
        <Container size="lg" py="lg">
            <PlayServerDetail playServerId={playServerId} />
        </Container>
    )
}
