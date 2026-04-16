import { MainShell } from '@/components/main-shell'
import { Box } from '@mantine/core'
import { useActiveUser } from '../user/api/active-user.api'
import { LandingView } from './components/landing-view'
import { HomeView } from './components/home-view'

export function Component() {
    const [user] = useActiveUser()

    if (!user) return <LandingView />

    return (
        <MainShell>
            <Box mt="-0.25rem">
                <HomeView />
            </Box>
        </MainShell>
    )
}
