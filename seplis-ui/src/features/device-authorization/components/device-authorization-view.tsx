import { Box, Center, Flex, Paper, Stack, Title } from '@mantine/core'
import { DevicesIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { DeviceAuthorizationForm } from './device-authorization-form'
import { DeviceAuthorizationSuccess } from './device-authorization-success'

function normalizeCode(value: string) {
    return value.replace(/\D/g, '').slice(0, 6)
}

export function DeviceAuthorizationView() {
    const [searchParams] = useSearchParams()
    const [authorized, setAuthorized] = useState(false)
    const initialCode = normalizeCode(searchParams.get('code') ?? '')

    let content = (
        <DeviceAuthorizationForm
            initialCode={initialCode}
            onAuthorized={() => setAuthorized(true)}
        />
    )

    if (authorized) content = <DeviceAuthorizationSuccess />

    return (
        <Box py="xl">
            <Center>
                <Paper withBorder p="xl">
                    <Stack gap="lg">
                        <Flex gap="sm" align="center">
                            <DevicesIcon size={28} />
                            <Title order={1} fz="h2">
                                Authorize a device
                            </Title>
                        </Flex>
                        {content}
                    </Stack>
                </Paper>
            </Center>
        </Box>
    )
}
