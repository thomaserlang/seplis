import { Genre } from '@/types/genre.types'
import { Flex, Pill, Text } from '@mantine/core'
import classes from './media-info.module.css'

export interface MediaStatus {
    label: string
    dot: string
}

export interface MediaMetaItem {
    label: string
    value: string
    color?: string
}

export interface MediaStatItem {
    label: string
    value: string
}

export interface MediaInfoProps {
    posterUrl?: string
    accentHue?: number
    status?: MediaStatus
    title: string
    originalTitle?: string | null
    tagline?: string | null
    metaItems: MediaMetaItem[]
    genres: Genre[]
    plot?: string | null
    stats: MediaStatItem[]
}

export function MediaInfo({
    posterUrl,
    accentHue = 250,
    status,
    title,
    originalTitle,
    tagline,
    metaItems,
    genres,
    plot,
    stats,
}: MediaInfoProps) {
    return (
        <div
            className={classes.root}
            style={{ '--accent-hue': accentHue } as React.CSSProperties}
        >
            <div className={classes.posterPanel}>
                {posterUrl && (
                    <img src={posterUrl} alt="" className={classes.posterImg} />
                )}
                {status && (
                    <div className={classes.posterMeta}>
                        <Flex align="center" gap="0.4rem">
                            <span
                                className={classes.statusDot}
                                style={{ background: status.dot }}
                            />
                            <Text size="xs" fw={600} style={{ color: 'oklch(1 0 0 / 0.7)' }}>
                                {status.label}
                            </Text>
                        </Flex>
                    </div>
                )}
            </div>

            <div className={classes.infoPanel}>
                <div>
                    <Text fw={700} size="xl" lh={1.2}>
                        {title}
                    </Text>
                    {originalTitle && originalTitle !== title && (
                        <Text size="sm" c="dimmed" mt="0.2rem">
                            {originalTitle}
                        </Text>
                    )}
                    {tagline && (
                        <Text size="sm" c="dimmed" fs="italic" mt="0.25rem">
                            {tagline}
                        </Text>
                    )}
                </div>

                {metaItems.length > 0 && (
                    <>
                        <div className={classes.divider} />
                        <Flex gap="1.25rem" wrap="wrap">
                            {metaItems.map((item) => (
                                <Flex key={item.label} direction="column" gap="0.1rem">
                                    <Text size="xs" c="dimmed" tt="uppercase" fw={600} lts="0.05em">
                                        {item.label}
                                    </Text>
                                    <Text
                                        size="sm"
                                        fw={item.color ? 700 : 600}
                                        style={item.color ? { color: item.color } : undefined}
                                    >
                                        {item.value}
                                    </Text>
                                </Flex>
                            ))}
                        </Flex>
                    </>
                )}

                {genres.length > 0 && (
                    <>
                        <div className={classes.divider} />
                        <Flex gap="0.35rem" wrap="wrap">
                            {genres.map((g) => (
                                <Pill key={g.id} size="sm" fw={600}>
                                    {g.name}
                                </Pill>
                            ))}
                        </Flex>
                    </>
                )}

                {plot && (
                    <>
                        <div className={classes.divider} />
                        <Text size="sm" c="dimmed" style={{ lineHeight: 1.75, flex: 1 }}>
                            {plot}
                        </Text>
                    </>
                )}

                {stats.length > 0 && (
                    <>
                        <div className={classes.divider} />
                        <Flex gap="0.6rem">
                            {stats.map((s) => (
                                <div key={s.label} className={classes.statBox}>
                                    <Text fw={800} size="xl" lh={1}>
                                        {s.value}
                                    </Text>
                                    <Text size="xs" c="dimmed" fw={500}>
                                        {s.label}
                                    </Text>
                                </div>
                            ))}
                        </Flex>
                    </>
                )}
            </div>
        </div>
    )
}
