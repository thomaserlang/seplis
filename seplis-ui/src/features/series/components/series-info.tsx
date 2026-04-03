import { Flex, Pill, Text } from '@mantine/core'
import { langCodeToLang } from '@/utils/language.utils'
import { Series } from '../types/series.types'
import classes from './series-info.module.css'

interface Props {
    series: Series
}

const STATUS: Record<number, { label: string; dot: string }> = {
    0: { label: 'Unknown', dot: 'oklch(0.6 0 0)' },
    1: { label: 'Returning', dot: 'oklch(0.7 0.17 175)' },
    2: { label: 'Ended', dot: 'oklch(0.6 0.2 25)' },
    3: { label: 'Cancelled', dot: 'oklch(0.7 0.18 55)' },
    4: { label: 'In production', dot: 'oklch(0.6 0.2 250)' },
    5: { label: 'Planned', dot: 'oklch(0.55 0.22 295)' },
}

export function SeriesInfo({ series }: Props) {
    const startYear = series.premiered?.substring(0, 4)
    const endYear = series.ended?.substring(0, 4)
    const yearRange = startYear
        ? endYear && endYear !== startYear
            ? `${startYear}–${endYear}`
            : startYear
        : null

    const status = series.status != null ? STATUS[series.status] : null

    const metaItems = [
        yearRange ? { label: 'Year', value: yearRange } : null,
        series.runtime ? { label: 'Runtime', value: `${series.runtime} min / ep` } : null,
        series.language ? { label: 'Language', value: langCodeToLang(series.language) } : null,
    ].filter(Boolean) as { label: string; value: string }[]

    return (
        <div className={classes.root}>
            {/* ── Left: Poster panel ── */}
            <div className={classes.posterPanel}>
                {series.poster_image && (
                    <img
                        src={`${series.poster_image.url}@SX320.webp`}
                        alt=""
                        className={classes.posterImg}
                    />
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

            {/* ── Right: Info panel ── */}
            <div className={classes.infoPanel}>
                {/* Title */}
                <div>
                    <Text fw={700} size="xl" lh={1.2}>
                        {series.title || series.original_title || 'Unknown title'}
                    </Text>
                    {series.original_title && series.original_title !== series.title && (
                        <Text size="sm" c="dimmed" mt="0.2rem">
                            {series.original_title}
                        </Text>
                    )}
                    {series.tagline && (
                        <Text size="sm" c="dimmed" fs="italic" mt="0.25rem">
                            {series.tagline}
                        </Text>
                    )}
                </div>

                {/* Meta row */}
                {metaItems.length > 0 && (
                    <>
                        <div className={classes.divider} />
                        <Flex gap="1.25rem" wrap="wrap">
                            {metaItems.map((item) => (
                                <Flex key={item.label} direction="column" gap="0.1rem">
                                    <Text size="xs" c="dimmed" tt="uppercase" fw={600} lts="0.05em">
                                        {item.label}
                                    </Text>
                                    <Text size="sm" fw={600}>
                                        {item.value}
                                    </Text>
                                </Flex>
                            ))}
                            {series.rating != null && (
                                <Flex direction="column" gap="0.1rem">
                                    <Text size="xs" c="dimmed" tt="uppercase" fw={600} lts="0.05em">
                                        Rating
                                    </Text>
                                    <Text size="sm" fw={700} style={{ color: 'oklch(0.82 0.18 85)' }}>
                                        ★ {series.rating.toFixed(1)}
                                    </Text>
                                </Flex>
                            )}
                        </Flex>
                    </>
                )}

                {/* Genres */}
                {series.genres.length > 0 && (
                    <>
                        <div className={classes.divider} />
                        <Flex gap="0.35rem" wrap="wrap">
                            {series.genres.map((g) => (
                                <Pill key={g.id} size="sm" fw={600}>
                                    {g.name}
                                </Pill>
                            ))}
                        </Flex>
                    </>
                )}

                {/* Plot */}
                {series.plot && (
                    <>
                        <div className={classes.divider} />
                        <Text size="sm" c="dimmed" style={{ lineHeight: 1.75, flex: 1 }}>
                            {series.plot}
                        </Text>
                    </>
                )}

                {/* Stats */}
                {(series.seasons.length > 0 || series.total_episodes > 0) && (
                    <>
                        <div className={classes.divider} />
                        <Flex gap="0.6rem">
                            {series.seasons.length > 0 && (
                                <div className={classes.statBox}>
                                    <Text fw={800} size="xl" lh={1}>
                                        {series.seasons.length}
                                    </Text>
                                    <Text size="xs" c="dimmed" fw={500}>
                                        {series.seasons.length === 1 ? 'Season' : 'Seasons'}
                                    </Text>
                                </div>
                            )}
                            {series.total_episodes > 0 && (
                                <div className={classes.statBox}>
                                    <Text fw={800} size="xl" lh={1}>
                                        {series.total_episodes}
                                    </Text>
                                    <Text size="xs" c="dimmed" fw={500}>
                                        Episodes
                                    </Text>
                                </div>
                            )}
                            {series.runtime != null && (
                                <div className={classes.statBox}>
                                    <Text fw={800} size="xl" lh={1}>
                                        {series.runtime}
                                    </Text>
                                    <Text size="xs" c="dimmed" fw={500}>
                                        Min / ep
                                    </Text>
                                </div>
                            )}
                        </Flex>
                    </>
                )}
            </div>
        </div>
    )
}
