import { MediaInfoModal } from '@/features/media-type/components/media-info-modal'
import { MediaPlayerModal } from '@/features/media-type/components/media-player-modal'
import { useActiveUser } from '@/features/user/api/active-user.api'
import { UserMenu } from '@/features/user/components/user-menu'
import { AppShell, Box, Button, Flex } from '@mantine/core'
import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { MainMenu } from './main-menu'

interface Props {
    children: ReactNode
}

export function MainShell({ children }: Props) {
    const [user] = useActiveUser()

    return (
        <AppShell padding="xs" header={{ height: 45 }}>
            <AppShell.Header>
                <Flex h="100%" align="center" p="0.5rem">
                    {user ? (
                        <>
                            <Flex gap="0.5rem">
                                <MainMenu />
                            </Flex>
                            <Box ml="auto">
                                <UserMenu />
                            </Box>
                        </>
                    ) : (
                        <>
                            <Box ml="auto">
                                <Flex gap="xs">
                                    <Button
                                        component={Link}
                                        to="/login"
                                        variant="subtle"
                                        size="compact-sm"
                                    >
                                        Log in
                                    </Button>
                                    <Button
                                        component={Link}
                                        to="/signup"
                                        size="compact-sm"
                                        radius="xl"
                                    >
                                        Sign up
                                    </Button>
                                </Flex>
                            </Box>
                        </>
                    )}
                </Flex>
            </AppShell.Header>
            <AppShell.Main>{children}</AppShell.Main>
            <MediaInfoModal />
            <MediaPlayerModal />
        </AppShell>
    )
}
