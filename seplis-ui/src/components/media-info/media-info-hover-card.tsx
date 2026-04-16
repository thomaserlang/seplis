import { Genre } from '@/features/genres/types/genre.types'
import { IImage } from '@/types/image.types'
import { Button, Flex, Text } from '@mantine/core'
import { CornersOutIcon } from '@phosphor-icons/react'
import { Genres } from '../genres'
import { MediaMetaItem } from './media-info'

export interface MediaInfoHoverCardProps {
    poster?: IImage | null
    accentHue?: number
    title: string
    originalTitle?: string | null
    metaItems: MediaMetaItem[]
    genres: Genre[]
    children?: React.ReactNode
    onInfoClick?: () => void
}

export function MediaInfoHoverCard({
    poster,
    accentHue = 250,
    title,
    originalTitle,
    metaItems,
    genres,
    children,
    onInfoClick,
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
                    cursor: onInfoClick ? 'pointer' : 'default',
                }}
                onClick={onInfoClick}
            >
                {poster && (
                    <img
                        src={`${poster.url}@SX320.webp`}
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            objectPosition: 'center top',
                            display: 'block',
                        }}
                    />
                )}
            </div>

            <Flex direction="column" gap="0.5rem" p="0.75rem" pt="0.5rem">
                <Flex direction="column">
                    <Flex align="center" justify="space-between" gap="0.5rem">
                        <Text
                            fw={700}
                            size="sm"
                            lh={1.25}
                            onClick={onInfoClick}
                            style={{
                                cursor: onInfoClick ? 'pointer' : 'default',
                            }}
                        >
                            {title || originalTitle}
                        </Text>
                        {onInfoClick && (
                            <Button
                                variant="default"
                                size="compact-sm"
                                px="0.4rem"
                                onClick={onInfoClick}
                                aria-label="More info"
                            >
                                <CornersOutIcon size={16} weight="bold" />
                            </Button>
                        )}
                    </Flex>
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
