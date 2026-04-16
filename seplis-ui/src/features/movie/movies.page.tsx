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
import { useGetMovies } from './api/movies.api'
import { MovieHoverCard } from './components/movie-hover-card'
import { MoviesFilterbar } from './components/movies-filterbar'
import { MovieUserSortType, MoviesGetParams } from './types/movies.types'

export function Component() {
    const [params, setParams] = useSearchParams()
    const sort = params
        .getAll('sort')
        .filter((v): v is MovieUserSortType => !!v) as MovieUserSortType[]
    const filter: MoviesGetParams = {
        sort: !isEmpty(sort) ? sort : ['popularity_desc'],
        genre_id: strListToNumList(params.getAll('genre_id')),
        not_genre_id: strListToNumList(params.getAll('not_genre_id')),
        user_can_watch: strToBoolUndefined(params.get('user_can_watch')),
        user_watchlist: strToBoolUndefined(params.get('user_watchlist')),
        user_favorites: strToBoolUndefined(params.get('user_favorites')),
        user_has_watched: strToBoolUndefined(params.get('user_has_watched')),
        release_date_gt: params.get('release_date_gt') ?? undefined,
        release_date_lt: params.get('release_date_lt') ?? undefined,
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
        useGetMovies({
            params: filter,
        })

    const items = pageItemsFlatten(data)

    return (
        <Flex direction="column" gap="0.25rem" mt="-0.5rem">
            <MoviesFilterbar
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
                renderItem={(movie) => (
                    <PosterImage
                        posterImage={movie.poster_image}
                        title={movie.title}
                    />
                )}
                renderHoverCard={(movie) => <MovieHoverCard movie={movie} />}
                onClick={(movie) => {
                    setParams((params) => {
                        params.set('mid', `movie-${movie.id}`)
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
