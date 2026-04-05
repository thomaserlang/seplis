import { Badge, Box, Flex, Paper, Skeleton, Text } from '@mantine/core'
import { TelevisionSimpleIcon } from '@phosphor-icons/react'
import { Episode } from '../types/episode.types'
import { EpisodePlayButton } from './episode-play-button'
import { EpisodeWatchedButton } from './episode-watched-button'

interface Props {
    seriesId: number
    episode: Episode | null | undefined
    loading: boolean
    title?: string
    accentColor?: string
    noEpisodeText?: string
}

export function EpisodeCard({
    seriesId,
    episode,
    loading,
    title,
    accentColor = 'oklch(0.55 0.22 250)',
    noEpisodeText,
}: Props) {
    if (loading) {
        return (
            <Box>
                <SectionTitle title={title} />
                <Paper withBorder p="sm" miw={220}>
                    <Flex direction="column" gap="xs">
                        <Skeleton height={18} width={60} radius="xl" />
                        <Skeleton height={14} width="80%" />
                        <Skeleton height={12} width={100} />
                        <Flex gap="xs" mt={4}>
                            <Skeleton height={30} width={90} radius="sm" />
                            <Skeleton height={30} width={90} radius="sm" />
                        </Flex>
                    </Flex>
                </Paper>
            </Box>
        )
    }

    if (!episode) {
        return (
            <Box>
                <SectionTitle title={title} />
                <Paper withBorder p="sm">
                    <Flex align="center" gap="sm" c="dimmed">
                        <TelevisionSimpleIcon size={28} />
                        <Text size="sm">
                            {noEpisodeText || 'No episode to watch'}
                        </Text>
                    </Flex>
                </Paper>
            </Box>
        )
    }

    const episodeLabel =
        episode.season != null && episode.episode != null
            ? `S${episode.season}E${episode.episode}`
            : `Ep ${episode.number}`

    return (
        <Box>
            <SectionTitle title={title} />
            <Paper
                withBorder
                p="sm"
                style={{ borderLeft: `3px solid ${accentColor}` }}
            >
                <Flex direction="column" gap="xs">
                    <Flex align="center" gap="xs">
                        <Badge
                            size="sm"
                            variant="light"
                            color="blue"
                            style={{ flexShrink: 0 }}
                        >
                            {episodeLabel}
                        </Badge>
                        {episode.air_date && (
                            <Text size="xs" c="dimmed" truncate>
                                {episode.air_date}
                            </Text>
                        )}
                    </Flex>

                    <Box>
                        <Text size="sm" fw={600} lineClamp={2}>
                            {episode.title || 'Untitled'}
                        </Text>
                        {episode.runtime && (
                            <Text size="xs" c="dimmed" mt={2}>
                                {episode.runtime} min
                            </Text>
                        )}
                    </Box>

                    <Flex gap="xs" wrap="wrap">
                        <EpisodePlayButton
                            seriesId={seriesId}
                            episodeNumber={episode.number}
                        />
                        <EpisodeWatchedButton
                            seriesId={seriesId}
                            episodeId={episode.number}
                        />
                    </Flex>
                </Flex>
            </Paper>
        </Box>
    )
}

function SectionTitle({ title }: { title?: string }) {
    if (!title) return null
    return (
        <Text size="xs" tt="uppercase" fw={700} c="dimmed" mb={6} lts={0.5}>
            {title}
        </Text>
    )
}
