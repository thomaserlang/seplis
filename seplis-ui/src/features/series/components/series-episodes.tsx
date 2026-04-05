import { PageLoader } from '@/components/page-loader'
import {
    EpisodePlayButton,
    EpisodeWatchedButton,
    useGetEpisodes,
} from '@/features/series-episode'
import { getActiveUser } from '@/features/user'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Flex, Select, Text } from '@mantine/core'
import { useState } from 'react'
import { Series } from '../types/series.types'
import classes from './series-episodes.module.css'

interface Props {
    series: Series
}

export function SeriesEpisodes({ series }: Props) {
    const user = getActiveUser()
    const [season, setSeason] = useState(series.seasons[0]?.season ?? 1)
    const { data, isLoading } = useGetEpisodes({
        seriesId: series.id,
        params: {
            season,
            per_page: 100,
            expand: user ? 'user_watched,user_can_watch' : undefined,
        },
    })

    const episodes = pageItemsFlatten(data)

    const seasonOptions = series.seasons.map((s) => ({
        value: String(s.season),
        label: `Season ${s.season}`,
    }))

    return (
        <div className={classes.root}>
            <Flex
                justify="space-between"
                align="center"
                className={classes.header}
            >
                <Text fw={600} size="sm">
                    Episodes
                </Text>
                {seasonOptions.length > 1 && (
                    <Select
                        value={String(season)}
                        onChange={(v) => v && setSeason(Number(v))}
                        data={seasonOptions}
                        size="xs"
                        w={120}
                        allowDeselect={false}
                    />
                )}
            </Flex>

            {isLoading && <PageLoader />}

            {!isLoading && (
                <div className={classes.list}>
                    {episodes.map((ep) => (
                        <div key={ep.number} className={classes.episode}>
                            <div className={classes.epNumber}>
                                <Text size="sm" fw={700} c="dimmed" lh={1.2}>
                                    {ep.episode ?? ep.number}
                                </Text>
                                {ep.episode != null &&
                                    ep.episode !== ep.number && (
                                        <Text
                                            size="xs"
                                            c="dimmed"
                                            lh={1}
                                            style={{ opacity: 0.45 }}
                                        >
                                            {ep.number}
                                        </Text>
                                    )}
                            </div>
                            <div className={classes.epMain}>
                                <Text size="sm" fw={600} lh={1.3}>
                                    {ep.title ||
                                        `Episode ${ep.episode ?? ep.number}`}
                                </Text>
                                {ep.plot && (
                                    <Text
                                        size="xs"
                                        c="dimmed"
                                        lineClamp={2}
                                        mt="0.2rem"
                                    >
                                        {ep.plot}
                                    </Text>
                                )}

                                <Flex
                                    mt="0.25rem"
                                    gap="0.5rem"
                                    direction="row"
                                    wrap="wrap"
                                    w="100%"
                                >
                                    <EpisodePlayButton
                                        size="compact-xs"
                                        seriesId={series.id}
                                        episodeNumber={ep.number}
                                        canPlay={
                                            ep.user_can_watch?.on_play_server
                                        }
                                    />
                                    <EpisodeWatchedButton
                                        seriesId={series.id}
                                        episodeNumber={ep.number}
                                        episode={ep}
                                        size="compact-xs"
                                    />
                                </Flex>
                            </div>
                            <Flex
                                direction="column"
                                align="flex-end"
                                gap="0.2rem"
                                className={classes.epMeta}
                            >
                                {ep.air_date && (
                                    <Text size="xs" c="dimmed">
                                        {ep.air_date.substring(0, 10)}
                                    </Text>
                                )}
                                {ep.runtime && (
                                    <Text size="xs" c="dimmed">
                                        {ep.runtime} min
                                    </Text>
                                )}
                            </Flex>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
