import { PosterImage } from '@/components/poster-image'
import { PosterPage } from '@/components/poster-page'
import { pageItemsFlatten } from '@/utils/api-crud'
import {
    isEmpty,
    strListToNumList,
    strToBoolUndefined,
} from '@/utils/str.utils'
import { Flex } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'
import { useGetSeriesList } from './api/series-list.api'
import { SeriesFilterbar } from './components/series-filterbar'
import { SeriesHoverCard } from './components/series-hover-card'
import {
    SeriesListGetParams,
    SeriesUserSortType,
} from './types/series-list.types'

export function Component() {
    const [params, setParams] = useSearchParams()

    const sort = params
        .getAll('sort')
        .filter((v): v is SeriesUserSortType => !!v) as SeriesUserSortType[]
    const filter: SeriesListGetParams = {
        sort: !isEmpty(sort) ? sort : ['popularity_desc'],
        genre_id: strListToNumList(params.getAll('genre_id')),
        not_genre_id: strListToNumList(params.getAll('not_genre_id')),
        user_can_watch: strToBoolUndefined(params.get('user_can_watch')),
        user_watchlist: strToBoolUndefined(params.get('user_watchlist')),
        user_favorites: strToBoolUndefined(params.get('user_favorites')),
        user_has_watched: strToBoolUndefined(params.get('user_has_watched')),
        premiered_gt: params.get('premiered_gt') ?? undefined,
        premiered_lt: params.get('premiered_lt') ?? undefined,
        rating_gt: params.get('rating_gt')
            ? Number(params.get('rating_gt'))
            : undefined,
        rating_lt: params.get('rating_lt')
            ? Number(params.get('rating_lt'))
            : undefined,
        rating_votes_gt: params.get('rating_votes_gt')
            ? Number(params.get('rating_votes_gt'))
            : undefined,
        rating_votes_lt: params.get('rating_votes_lt')
            ? Number(params.get('rating_votes_lt'))
            : undefined,
        language: params.getAll('language'),
    }

    const { data, isLoading, fetchNextPage, isFetchingNextPage, hasNextPage } =
        useGetSeriesList({ params: filter })

    const items = pageItemsFlatten(data)

    return (
        <Flex direction="column" mt="-0.75rem">
            <SeriesFilterbar
                filter={filter}
                setFilter={(f) => {
                    setParams((params) => {
                        Object.entries(f).forEach(([key, value]) => {
                            if (isEmpty(value)) {
                                params.delete(key)
                            } else {
                                if (Array.isArray(value)) {
                                    params.delete(key)
                                    value.forEach((v) =>
                                        params.append(key, String(v)),
                                    )
                                    return
                                }
                                params.set(key, value)
                            }
                        })
                        return params
                    })
                }}
            />

            <PosterPage
                items={items}
                renderItem={(series) => (
                    <PosterImage
                        posterImage={series.poster_image}
                        title={series.title}
                    />
                )}
                renderHoverCard={(series) => (
                    <SeriesHoverCard series={series} />
                )}
                onClick={(series) => {
                    setParams((params) => {
                        params.set('mid', `series-${series.id}`)
                        return params
                    })
                }}
                onLoadMore={fetchNextPage}
                hasMore={hasNextPage}
                isLoading={isLoading || isFetchingNextPage}
            />
        </Flex>
    )
}
