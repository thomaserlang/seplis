import { useHoverCard } from '@/components/hover-card/use-hover-card'
import { PosterImage } from '@/components/poster-image/poster-image'
import classes from '@/components/poster-page.module.css'
import { pageItemsFlatten } from '@/utils/api-crud'
import {
    isEmpty,
    strListToNumList,
    strToBoolUndefined,
} from '@/utils/str.utils'
import { Flex, Loader } from '@mantine/core'
import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useGetSeriesList } from './api/series-list.api'
import { SeriesFilterbar } from './components/series-filterbar'
import { SeriesHoverCard } from './components/series-hover-card'
import {
    SeriesListGetParams,
    SeriesUserSortType,
} from './types/series-list.types'
import { Series } from './types/series.types'

export function Component() {
    const [params, setParams] = useSearchParams()

    const filter: SeriesListGetParams = {
        sort: params
            .getAll('sort')
            .filter(
                (v): v is SeriesUserSortType => !!v,
            ) as SeriesUserSortType[],
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

    const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
        useGetSeriesList({ params: filter })

    const items = pageItemsFlatten(data)
    const { getItemProps, portal } = useHoverCard<Series>((series) => (
        <SeriesHoverCard series={series} />
    ))
    const sentinelRef = useRef<HTMLDivElement>(null)
    const canFetchRef = useRef(false)
    canFetchRef.current = hasNextPage && !isFetchingNextPage

    useEffect(() => {
        const el = sentinelRef.current
        if (!el) return
        const ob = new IntersectionObserver(
            ([e]) => {
                if (e.isIntersecting && canFetchRef.current) fetchNextPage()
            },
            { rootMargin: '0px 0px 400px 0px' },
        )
        ob.observe(el)
        return () => ob.disconnect()
    }, [fetchNextPage])

    return (
        <Flex direction="column" gap="1rem">
            <div className={classes.filterBar}>
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
            </div>
            {isLoading ? (
                <Loader m="auto" mt="xl" />
            ) : (
                <div className={classes.grid}>
                    {items.map((series) => (
                        <div
                            key={series.id}
                            className={classes.item}
                            onClick={() =>
                                setParams((params) => {
                                    params.set('mid', `series-${series.id}`)
                                    return params
                                })
                            }
                            {...getItemProps(series)}
                        >
                            <PosterImage
                                posterImage={series.poster_image}
                                title={series.title}
                            />
                        </div>
                    ))}
                </div>
            )}

            <div ref={sentinelRef} />
            {portal}
        </Flex>
    )
}
