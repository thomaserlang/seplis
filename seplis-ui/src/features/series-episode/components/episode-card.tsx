import {
    Badge,
    Box,
    ButtonSize,
    Flex,
    MantineFontSize,
    Paper,
    Skeleton,
    Text,
} from '@mantine/core'
import { TelevisionSimpleIcon } from '@phosphor-icons/react'
import { Episode } from '../types/episode.types'
import { EpisodePlayButton } from './episode-play-button'
import { EpisodeWatchedButton } from './episode-watched-button'

export interface EpisodeCardProps {
    seriesId: number
    episode: Episode | null | undefined
    loading: boolean
    title?: string
    accentColor?: string
    noEpisodeText?: string
    buttonSize?: ButtonSize
    fz?: MantineFontSize
}

export function EpisodeCard({
    seriesId,
    episode,
    loading,
    title,
    accentColor = 'oklch(0.55 0.22 250)',
    noEpisodeText,
    buttonSize,
    ...props
}: EpisodeCardProps) {
    return (
        <Box>
            {title && (
                <Text
                    size="xs"
                    tt="uppercase"
                    fw={700}
                    c="dimmed"
                    mb={6}
                    lts={0.5}
                >
                    {title}
                </Text>
            )}
            {loading && <EpisodeCardSkeleton />}
            {!loading && !episode && (
                <EpisodeCardEmpty fz={props.fz} noEpisodeText={noEpisodeText} />
            )}
            {!loading && episode && (
                <EpisodeCardContent
                    {...props}
                    seriesId={seriesId}
                    episode={episode}
                    accentColor={accentColor}
                    buttonSize={buttonSize}
                />
            )}
        </Box>
    )
}

function EpisodeCardSkeleton() {
    return (
        <Paper withBorder p="sm">
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
    )
}

function EpisodeCardEmpty({
    fz = 'sm',
    noEpisodeText,
}: {
    fz?: MantineFontSize
    noEpisodeText?: string
}) {
    return (
        <Paper withBorder p="sm">
            <Flex align="center" gap="sm" c="dimmed">
                <TelevisionSimpleIcon size={28} />
                <Text size={fz}>{noEpisodeText || 'No episode to watch'}</Text>
            </Flex>
        </Paper>
    )
}

function EpisodeCardContent({
    seriesId,
    episode,
    accentColor,
    buttonSize,
    fz = 'md',
}: Partial<EpisodeCardProps> & { seriesId: number; episode: Episode }) {
    const episodeLabel =
        episode.season != null && episode.episode != null
            ? `S${episode.season}E${episode.episode}`
            : `Ep ${episode.number}`

    return (
        <Paper
            withBorder
            p="0.5rem"
            style={{ borderLeft: `3px solid ${accentColor}` }}
        >
            <Flex direction="column" gap="0.25rem">
                <Flex align="center" gap="xs">
                    <Badge size="md" variant="light" color="blue">
                        {episodeLabel}
                    </Badge>
                    {episode.air_date && (
                        <Text size="sm" c="dimmed" truncate>
                            {episode.air_date}
                        </Text>
                    )}
                </Flex>

                <Box>
                    <Text
                        size={fz}
                        fw={600}
                        title={episode.title || ''}
                        truncate
                    >
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
                        canPlay={episode.user_can_watch?.on_play_server}
                        size={buttonSize}
                    />
                    <EpisodeWatchedButton
                        seriesId={seriesId}
                        episodeNumber={episode.number}
                        episode={episode}
                        size={buttonSize}
                    />
                </Flex>
            </Flex>
        </Paper>
    )
}
