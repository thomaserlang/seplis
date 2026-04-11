import { useActiveUser } from '@/features/user'
import { Button, Flex, Paper, Text } from '@mantine/core'
import { Link } from 'react-router-dom'
import { useGetEpisodeToWatch } from '../api/episode-to-watch.api'
import { EpisodeCard } from './episode-card'

interface Props {
    seriesId: number
}

export function EpisodeToWatchCard({ seriesId }: Props) {
    const [user] = useActiveUser()
    const { data, isLoading } = useGetEpisodeToWatch({
        seriesId,
        options: {
            enabled: !!user,
        },
    })

    if (!user)
        return (
            <Paper withBorder p="sm">
                <Flex align="center" justify="space-between" gap="sm">
                    <Text size="sm" c="dimmed">
                        Sign in to track and watch episodes
                    </Text>
                    <Button
                        component={Link}
                        to="/login"
                        size="compact-sm"
                        variant="primary"
                    >
                        Sign in
                    </Button>
                </Flex>
            </Paper>
        )

    return (
        <EpisodeCard
            seriesId={seriesId}
            episode={data}
            loading={isLoading}
            title={
                !data?.user_watched?.position
                    ? 'Next to watch'
                    : 'Continue watching'
            }
            accentColor="oklch(0.65 0.13 65)"
            noEpisodeText="No episode to watch"
        />
    )
}
