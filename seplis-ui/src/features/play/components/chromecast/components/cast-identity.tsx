import { Logo } from '@/components/logo'
import { Stack, Text } from '@mantine/core'
import type { ReactNode } from 'react'

interface Props {
    deviceName: string
    playerState: string | null
    title?: string
    secondaryTitle?: string
}

export function CastIdentity({
    deviceName,
    playerState,
    title,
    secondaryTitle,
}: Props): ReactNode {
    return (
        <>
            <Stack align="center" gap="xs">
                <Logo mb="1rem" />
                <Text
                    size="xs"
                    c="dimmed"
                    tt="uppercase"
                    fw={600}
                    style={{ letterSpacing: '0.08em' }}
                >
                    Casting to
                </Text>
                <Text fw={700} size="xl">
                    {deviceName}
                </Text>
                {playerState && (
                    <Text size="xs" c="dimmed">
                        {playerState}
                    </Text>
                )}
            </Stack>

            {title && (
                <Stack
                    align="center"
                    gap={4}
                    style={{ maxWidth: 360, width: '100%' }}
                >
                    <Text fw={600} size="lg" ta="center" lineClamp={2}>
                        {title}
                    </Text>
                    {secondaryTitle && (
                        <Text size="sm" c="dimmed" ta="center">
                            {secondaryTitle}
                        </Text>
                    )}
                </Stack>
            )}
        </>
    )
}
