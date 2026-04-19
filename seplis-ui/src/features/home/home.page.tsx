import { Box } from '@mantine/core'
import { useActiveUser } from '../user/api/session.store'
import { HomeView } from './components/home-view'
import { LandingView } from './components/landing-view'

export function Component() {
    const [user] = useActiveUser()

    if (!user) return <LandingView />

    return (
        <Box mt="-0.25rem">
            <HomeView />
        </Box>
    )
}
