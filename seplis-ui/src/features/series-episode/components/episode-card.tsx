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

export type EpisodeCardSize = 'sm' | 'md'

export interface EpisodeCardProps {
    seriesId: number
    episode: Episode | null | undefined
    loading: boolean
    title?: string
    accentColor?: string
    noEpisodeText?: string
    buttonSize?: ButtonSize
    fz?: MantineFontSize
    size?: EpisodeCardSize
}

export function EpisodeCard({
    seriesId,
    episode,
    loading,
    title,
    accentColor = 'oklch(0.55 0.22 250)',
    noEpisodeText,
    buttonSize,
    size,
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
            {loading && <EpisodeCardSkeleton size={size} />}
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

export function EpisodeCardSkeleton({
    size = 'md',
}: {
    size?: EpisodeCardSize
}) {
    const sm = size === 'sm'
    return (
        <Paper withBorder p={sm ? '0.4rem' : '0.5rem'}>
            <Flex direction="column" gap={sm ? 5 : 'xs'}>
                <Skeleton height={sm ? 14 : 18} width={55} radius="xl" />
                <Skeleton height={sm ? 12 : 14} width="80%" />
                <Flex gap="xs" mt={2}>
                    <Skeleton height={sm ? 26 : 30} width={85} radius="sm" />
                    <Skeleton height={sm ? 26 : 30} width={85} radius="sm" />
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

                <Flex gap="0.5rem" wrap="wrap">
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
