import { useHoverCard } from '@/components/hover-card/use-hover-card'
import { PosterImage } from '@/components/poster-image/poster-image'
import classes from '@/components/poster-page.module.css'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Chip, Flex, Loader, Select } from '@mantine/core'
import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useGetSeriesList } from './api/series-list.api'
import { SeriesHoverCard } from './components/series-hover-card'
import { SeriesListGetParams, SeriesUserSortType } from './types/series-list.types'
import { Series } from './types/series.types'

const SORT_OPTIONS: { value: SeriesUserSortType; label: string }[] = [
    { value: 'popularity_desc', label: 'Popular' },
    { value: 'premiered_desc', label: 'Newest' },
    { value: 'premiered_asc', label: 'Oldest' },
    { value: 'rating_desc', label: 'Top Rated' },
    { value: 'user_play_server_series_added_desc', label: 'Recently Added' },
    { value: 'user_last_episode_watched_at_desc', label: 'Recently Watched' },
    { value: 'user_watchlist_added_at_desc', label: 'Watchlist Added' },
    { value: 'user_favorite_added_at_desc', label: 'Favorites Added' },
]

export function Component() {
    const [params, setParams] = useSearchParams()

    const sort = (params.get('sort') as SeriesUserSortType) ?? 'popularity_desc'
    const userCanWatch = params.get('user_can_watch') === '1'
    const userWatchlist = params.get('user_watchlist') === '1'
    const userFavorites = params.get('user_favorites') === '1'
    const unwatchedOnly = params.get('user_has_watched') === 'false'

    function set(key: string, value: string | null) {
        setParams((prev) => {
            const next = new URLSearchParams(prev)
            if (value === null) next.delete(key)
            else next.set(key, value)
            return next
        })
    }

    const filter: SeriesListGetParams = {
        sort: [sort],
        user_can_watch: userCanWatch || undefined,
        user_watchlist: userWatchlist || undefined,
        user_favorites: userFavorites || undefined,
        user_has_watched: unwatchedOnly ? false : undefined,
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
            <Flex gap="0.5rem" wrap="wrap" align="center">
                <Select
                    size="xs"
                    value={sort}
                    onChange={(v) => set('sort', v)}
                    data={SORT_OPTIONS}
                    w={170}
                    allowDeselect={false}
                />
                <Chip
                    size="xs"
                    checked={userCanWatch}
                    onChange={(v) => set('user_can_watch', v ? '1' : null)}
                >
                    Available
                </Chip>
                <Chip
                    size="xs"
                    checked={userWatchlist}
                    onChange={(v) => set('user_watchlist', v ? '1' : null)}
                >
                    Watchlist
                </Chip>
                <Chip
                    size="xs"
                    checked={userFavorites}
                    onChange={(v) => set('user_favorites', v ? '1' : null)}
                >
                    Favorites
                </Chip>
                <Chip
                    size="xs"
                    checked={unwatchedOnly}
                    onChange={(v) => set('user_has_watched', v ? 'false' : null)}
                >
                    Unwatched
                </Chip>
            </Flex>

            {isLoading ? (
                <Loader m="auto" mt="xl" />
            ) : (
                <div className={classes.grid}>
                    {items.map((series) => (
                        <div
                            key={series.id}
                            className={classes.item}
                            onClick={() => set('mid', `series-${series.id}`)}
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
