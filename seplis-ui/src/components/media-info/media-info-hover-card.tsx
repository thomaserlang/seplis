import { Genre } from '@/types/genre.types'
import { Flex, Text } from '@mantine/core'
import { Genres } from '../genres'
import { MediaMetaItem } from './media-info'

export interface MediaInfoHoverCardProps {
    posterUrl?: string
    accentHue?: number
    title: string
    originalTitle?: string | null
    metaItems: MediaMetaItem[]
    genres: Genre[]
    children?: React.ReactNode
}

export function MediaInfoHoverCard({
    posterUrl,
    accentHue = 250,
    title,
    originalTitle,
    metaItems,
    genres,
    children,
}: MediaInfoHoverCardProps) {
    return (
        <div
            style={
                {
                    '--accent-hue': accentHue,
                    background: `linear-gradient(155deg, color-mix(in oklab, var(--card) 85%, oklch(0.55 0.18 ${accentHue})) 0%, var(--card) 55%)`,
                } as React.CSSProperties
            }
        >
            <div
                style={{
                    width: '100%',
                    height: '7rem',
                    overflow: 'hidden',
                }}
            >
                <img
                    src={posterUrl}
                    style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        objectPosition: 'center top',
                        display: 'block',
                    }}
                />
            </div>

            <Flex direction="column" gap="0.5rem" p="0.75rem" pt="0.5rem">
                <Flex direction="column">
                    <Text fw={700} size="sm" lh={1.25}>
                        {title || originalTitle}
                    </Text>
                    {metaItems && metaItems.length > 0 && (
                        <Text size="xs" c="dimmed">
                            {metaItems.map((item) => item.value).join(' · ')}
                        </Text>
                    )}
                    <Genres genres={genres} size="xs" />
                </Flex>
                {children}
            </Flex>
        </div>
    )
}
