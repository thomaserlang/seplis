import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import {
    EpisodePlayButton,
    EpisodeWatchedButton,
    useGetEpisodes,
} from '@/features/series-episode'
import { useActiveUser } from '@/features/user'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Button, Center, Flex, Text } from '@mantine/core'
import classes from './series-episodes.module.css'

interface Props {
    seriesId: number
    season?: number
    loadMoreButton?: boolean
}

export function SeriesEpisodes({
    seriesId,
    season = 1,
    loadMoreButton,
}: Props) {
    const [user] = useActiveUser()
    const {
        data,
        isLoading,
        isFetchingNextPage,
        fetchNextPage,
        error,
        hasNextPage,
    } = useGetEpisodes({
        seriesId: seriesId,
        params: {
            season,
            per_page: 100,
            expand: user ? 'user_watched,user_can_watch' : undefined,
        },
    })

    const episodes = pageItemsFlatten(data)

    return (
        <>
            {(isLoading || isFetchingNextPage) && <PageLoader />}

            {error && !data && <ErrorBox errorObj={error} />}

            {episodes.map((ep) => (
                <div key={ep.number} className={classes.episode}>
                    <div className={classes.epNumber}>
                        <Text size="sm" fw={700} c="dimmed">
                            {ep.episode ?? ep.number}
                        </Text>
                        {ep.episode != null && ep.episode !== ep.number && (
                            <Text size="xs" c="dimmed">
                                {ep.number}
                            </Text>
                        )}
                    </div>
                    <div className={classes.epMain}>
                        <Text size="sm" fw={600}>
                            {ep.title || `Episode ${ep.episode ?? ep.number}`}
                        </Text>
                        {ep.plot && (
                            <Text size="xs" c="dimmed">
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
                                size="compact-sm"
                                seriesId={seriesId}
                                episodeNumber={ep.number}
                                canPlay={ep.user_can_watch?.on_play_server}
                            />
                            <EpisodeWatchedButton
                                seriesId={seriesId}
                                episodeNumber={ep.number}
                                episode={ep}
                                size="compact-sm"
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

            <Center mt="1rem">
                {loadMoreButton && !isFetchingNextPage && hasNextPage && (
                    <Button variant="default" onClick={() => fetchNextPage()}>
                        Load more
                    </Button>
                )}
            </Center>
        </>
    )
}
