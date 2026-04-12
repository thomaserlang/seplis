import { Genre } from '@/types/genre.types'
import { Flex, Text } from '@mantine/core'
import { Genres } from '../genres'
import { MediaMetaItem } from './media-info'
import classes from './media-info.module.css'

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
        <div>
            <div
                className={classes.root}
                style={{ '--accent-hue': accentHue } as React.CSSProperties}
            >
                <div
                    style={{
                        width: '100%',
                        height: '5rem',
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
            </div>

            <Flex direction="column" gap="0.45rem" p="0.75rem">
                <Text fw={700} size="sm" lh={1.25}>
                    {title || originalTitle}
                </Text>
                {metaItems && metaItems.length > 0 && (
                    <Text size="xs" c="dimmed">
                        {metaItems.map((item) => item.value).join(' · ')}
                    </Text>
                )}
                <Genres genres={genres} size="xs" />
                {children}
            </Flex>
        </div>
    )
}
