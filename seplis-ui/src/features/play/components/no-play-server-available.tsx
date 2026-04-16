import { Logo } from '@/components/logo'
import { Box, Button, Container, Flex, Paper, Stack, Text } from '@mantine/core'
import {
    ArrowArcRightIcon,
    ArrowLeftIcon,
    HardDrivesIcon,
    LinkBreakIcon,
    MonitorPlayIcon,
} from '@phosphor-icons/react'

interface NoPlayServerAvailableProps {
    onBack: () => void
    onRetry: () => void
    loading?: boolean
}

export function NoPlayServerAvailable({
    onBack,
    onRetry,
    loading,
}: NoPlayServerAvailableProps) {
    return (
        <Container
            size="sm"
            py="xl"
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '2rem',
            }}
        >
            <Logo />
            <Paper
                radius="1.5rem"
                p={{ base: 'xl', sm: '2rem' }}
                withBorder
                style={{
                    width: '100%',
                    overflow: 'hidden',
                    position: 'relative',
                    background:
                        'linear-gradient(180deg, color-mix(in oklab, var(--card) 92%, white) 0%, var(--card) 100%)',
                    boxShadow: '0 1.5rem 4rem -2.5rem rgba(0, 0, 0, 0.45)',
                }}
            >
                <Box
                    style={{
                        position: 'absolute',
                        inset: 0,
                        pointerEvents: 'none',
                        background:
                            'radial-gradient(circle at top left, color-mix(in oklab, var(--primary) 12%, transparent) 0, transparent 34%), radial-gradient(circle at bottom right, color-mix(in oklab, var(--destructive) 15%, transparent) 0, transparent 30%)',
                    }}
                />

                <Stack gap="xl" align="center" style={{ position: 'relative' }}>
                    <InfrastructureIssueIllustration />

                    <Stack gap="sm" align="center" maw={420}>
                        <Text ta="center" size="1.75rem" fw={700} lh={1.1}>
                            No play server available
                        </Text>
                        <Text ta="center" c="dimmed" size="md">
                            There is currently no play server available to play
                            this content. Try again in a moment.
                        </Text>
                    </Stack>

                    <Flex gap="sm" wrap="wrap" justify="center">
                        <Button
                            variant="default"
                            size="md"
                            leftSection={<ArrowLeftIcon />}
                            onClick={onBack}
                        >
                            Back
                        </Button>
                        <Button
                            size="md"
                            leftSection={<ArrowArcRightIcon />}
                            onClick={onRetry}
                            loading={loading}
                        >
                            Try again
                        </Button>
                    </Flex>
                </Stack>
            </Paper>
        </Container>
    )
}

function InfrastructureIssueIllustration() {
    return (
        <Box
            aria-hidden
            style={{
                position: 'relative',
                width: '100%',
                maxWidth: '26rem',
                padding: '1rem 0 1.5rem',
            }}
        >
            <Box
                style={{
                    position: 'absolute',
                    inset: '8% 6% 18%',
                    borderRadius: '999px',
                    background:
                        'radial-gradient(circle, color-mix(in oklab, var(--primary) 12%, transparent) 0%, transparent 66%)',
                    border: '1px dashed color-mix(in oklab, var(--primary) 16%, var(--border))',
                }}
            />

            <Stack
                gap="lg"
                align="center"
                justify="center"
                style={{ position: 'relative', zIndex: 1 }}
            >
                <Flex
                    align="center"
                    justify="center"
                    gap="md"
                    wrap="nowrap"
                    style={{ width: '100%' }}
                >
                    <Paper
                        radius="1.5rem"
                        withBorder
                        p="lg"
                        style={{
                            width: '9rem',
                            background:
                                'linear-gradient(180deg, color-mix(in oklab, var(--card) 94%, white), var(--card))',
                            boxShadow:
                                '0 1rem 2rem -1.25rem rgba(0, 0, 0, 0.35)',
                        }}
                    >
                        <Stack gap="sm" align="center">
                            <MonitorPlayIcon size={60} weight="duotone" />
                            <Box
                                style={{
                                    width: '80%',
                                    height: '0.6rem',
                                    borderRadius: '999px',
                                    background:
                                        'linear-gradient(90deg, color-mix(in oklab, var(--primary) 70%, white), color-mix(in oklab, var(--primary) 28%, transparent))',
                                }}
                            />
                            <Box
                                style={{
                                    width: '56%',
                                    height: '0.5rem',
                                    borderRadius: '999px',
                                    background: 'var(--border)',
                                }}
                            />
                        </Stack>
                    </Paper>

                    <Stack gap="xs" align="center" w="5.5rem">
                        <Paper
                            radius="999px"
                            withBorder
                            p="sm"
                            style={{
                                background:
                                    'linear-gradient(180deg, color-mix(in oklab, var(--card) 96%, white), var(--card))',
                                boxShadow:
                                    '0 1rem 2rem -1.25rem rgba(0, 0, 0, 0.35)',
                            }}
                        >
                            <LinkBreakIcon
                                size={32}
                                weight="fill"
                                style={{
                                    color: 'color-mix(in oklab, var(--destructive) 86%, black)',
                                }}
                            />
                        </Paper>
                        <Box
                            style={{
                                width: '100%',
                                height: '0.3rem',
                                borderRadius: '999px',
                                background:
                                    'repeating-linear-gradient(90deg, color-mix(in oklab, var(--border) 90%, transparent) 0 0.7rem, transparent 0.7rem 1rem)',
                            }}
                        />
                    </Stack>

                    <Paper
                        radius="1.5rem"
                        withBorder
                        p="lg"
                        style={{
                            width: '9rem',
                            background:
                                'linear-gradient(180deg, color-mix(in oklab, var(--card) 94%, white), var(--card))',
                            boxShadow:
                                '0 1rem 2rem -1.25rem rgba(0, 0, 0, 0.35)',
                        }}
                    >
                        <Stack gap="xs" align="center">
                            <HardDrivesIcon size={54} weight="duotone" />
                            <Box
                                style={{
                                    width: '78%',
                                    height: '0.55rem',
                                    borderRadius: '999px',
                                    background:
                                        'linear-gradient(90deg, color-mix(in oklab, var(--foreground) 24%, transparent), color-mix(in oklab, var(--foreground) 10%, transparent))',
                                }}
                            />
                            <Flex gap="xs" justify="center">
                                <Box
                                    style={{
                                        width: '0.55rem',
                                        height: '0.55rem',
                                        borderRadius: '50%',
                                        background:
                                            'color-mix(in oklab, var(--destructive) 82%, white)',
                                    }}
                                />
                                <Box
                                    style={{
                                        width: '0.55rem',
                                        height: '0.55rem',
                                        borderRadius: '50%',
                                        background: 'var(--border)',
                                    }}
                                />
                                <Box
                                    style={{
                                        width: '0.55rem',
                                        height: '0.55rem',
                                        borderRadius: '50%',
                                        background: 'var(--border)',
                                    }}
                                />
                            </Flex>
                        </Stack>
                    </Paper>
                </Flex>
            </Stack>
        </Box>
    )
}
