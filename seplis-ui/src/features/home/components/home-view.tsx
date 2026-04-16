import { MediaType } from '@/features/media-type'
import { MoviesSlider } from '@/features/movie'
import {
    SeriesRecentlyAiredSlider,
    SeriesSlider,
    SeriesToWatchSlider,
} from '@/features/series'
import { Flex } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'
import { SliderWatched } from './slider-watched'

interface Props {}

export function HomeView({}: Props) {
    const [_, setParams] = useSearchParams()

    function handleClick(type: MediaType, itemId: number | string) {
        setParams((params) => {
            params.set('mid', `${type}-${itemId}`)
            return params
        })
    }

    return (
        <Flex direction="column" gap="0.25rem" mx="-0.5rem">
            <SliderWatched
                title="Watched"
                onClick={(item) => handleClick(item.type, item.data.id)}
            />
            <SeriesToWatchSlider
                title="Series to Watch"
                onClick={(item) => handleClick('series', item.series.id)}
                params={{
                    user_can_watch: true,
                }}
            />
            <MoviesSlider
                title="Movie watchlist"
                onClick={(item) => handleClick('movie', item.id)}
                params={{
                    user_watchlist: true,
                    user_can_watch: true,
                    sort: ['user_watchlist_added_at_desc'],
                }}
            />
            <SeriesSlider
                title="Series recently added"
                onClick={(item) => handleClick('series', item.id)}
                params={{
                    user_can_watch: true,
                    sort: ['user_play_server_series_added_desc'],
                }}
            />
            <MoviesSlider
                title="Movies recently added"
                onClick={(item) => handleClick('movie', item.id)}
                params={{
                    user_can_watch: true,
                    sort: ['user_play_server_movie_added_desc'],
                }}
            />
            <SeriesSlider
                title="Popular series"
                onClick={(item) => handleClick('series', item.id)}
                params={{
                    user_can_watch: true,
                    sort: ['popularity_desc'],
                }}
            />
            <MoviesSlider
                title="Popular movies"
                onClick={(item) => handleClick('movie', item.id)}
                params={{
                    user_can_watch: true,
                    sort: ['popularity_desc'],
                }}
            />
            <SeriesRecentlyAiredSlider
                title="Episodes recently aired"
                onClick={(item) => handleClick('series', item.series.id)}
                params={{
                    user_can_watch: true,
                    days_ahead: 7,
                }}
            />
            <SeriesSlider
                title="Series watchlist"
                onClick={(item) => handleClick('series', item.id)}
                params={{
                    user_watchlist: true,
                    user_can_watch: true,
                    sort: ['user_watchlist_added_at_desc'],
                }}
            />
            <SeriesSlider
                title="Series you haven't watched"
                onClick={(item) => handleClick('series', item.id)}
                params={{
                    user_has_watched: false,
                    user_can_watch: true,
                }}
            />
            <MoviesSlider
                title="Movies you haven't watched"
                onClick={(item) => handleClick('movie', item.id)}
                params={{
                    user_has_watched: false,
                    user_can_watch: true,
                }}
            />
            <SeriesSlider
                title="Series favorites"
                onClick={(item) => handleClick('series', item.id)}
                params={{
                    user_favorites: true,
                    user_can_watch: true,
                    sort: ['user_favorite_added_at_desc'],
                }}
            />
            <MoviesSlider
                title="Movie favorites"
                onClick={(item) => handleClick('movie', item.id)}
                params={{
                    user_favorites: true,
                    user_can_watch: true,
                    sort: ['user_favorite_added_at_desc'],
                }}
            />
        </Flex>
    )
}
