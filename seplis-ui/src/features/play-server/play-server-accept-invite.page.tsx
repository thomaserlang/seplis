import { Box, Center } from '@mantine/core'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { PlayServerAcceptInviteForm } from './components/play-server-accept-invite-form'

export function Component() {
    const navigate = useNavigate()
    const [params] = useSearchParams()

    return (
        <Box py="lg">
            <Center>
                <PlayServerAcceptInviteForm
                    initialInviteId={params.get('invite_id') ?? ''}
                    onAccepted={() => navigate('/')}
                />
            </Center>
        </Box>
    )
}
