import { UserMenu } from '@/features/user/components/user-menu'
import { AppShell, Box, Flex } from '@mantine/core'
import { ReactNode } from 'react'
import { MainMenu } from './main-menu'

interface Props {
    children: ReactNode
}

export function MainShell({ children }: Props) {
    return (
        <AppShell padding="md">
            <AppShell.Header>
                <Flex h="100%" align="center" p="0.5rem">
                    <Flex gap="0.5rem">
                        <MainMenu />
                    </Flex>
                    <Box ml="auto">
                        <UserMenu />
                    </Box>
                </Flex>
            </AppShell.Header>
            {children}
        </AppShell>
    )
}
