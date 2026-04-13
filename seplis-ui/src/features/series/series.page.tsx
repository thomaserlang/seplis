import { GenreFilter } from '@/components/genre-filter'
import { useHoverCard } from '@/components/hover-card/use-hover-card'
import { PosterImage } from '@/components/poster-image/poster-image'
import classes from '@/components/poster-page.module.css'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Button, Divider, Flex, Loader, Select } from '@mantine/core'
import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useGetSeriesList } from './api/series-list.api'
import { SeriesHoverCard } from './components/series-hover-card'
import {
    SeriesListGetParams,
    SeriesUserSortType,
} from './types/series-list.types'
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
    const genreIds =
        params.get('genre_id')?.split(',').map(Number).filter(Boolean) ?? []

    function set(key: string, value: string | null) {
        setParams((prev) => {
            const next = new URLSearchParams(prev)
            if (value === null) next.delete(key)
            else next.set(key, value)
            return next
        })
    }

    function setGenres(ids: number[]) {
        set('genre_id', ids.length ? ids.join(',') : null)
    }

    const filter: SeriesListGetParams = {
        sort: [sort],
        genre_id: genreIds.length ? genreIds : undefined,
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
            <div className={classes.filterBar}>
                <Select
                    size="xs"
                    value={sort}
                    onChange={(v) => set('sort', v)}
                    data={SORT_OPTIONS}
                    w={170}
                    allowDeselect={false}
                    radius="xl"
                />
                <Divider orientation="vertical" h={20} my="auto" />
                <Button
                    size="xs"
                    radius="xl"
                    variant={userCanWatch ? 'filled' : 'default'}
                    onClick={() =>
                        set('user_can_watch', userCanWatch ? null : '1')
                    }
                >
                    Available
                </Button>
                <Button
                    size="xs"
                    radius="xl"
                    variant={userWatchlist ? 'filled' : 'default'}
                    onClick={() =>
                        set('user_watchlist', userWatchlist ? null : '1')
                    }
                >
                    Watchlist
                </Button>
                <Button
                    size="xs"
                    radius="xl"
                    variant={userFavorites ? 'filled' : 'default'}
                    onClick={() =>
                        set('user_favorites', userFavorites ? null : '1')
                    }
                >
                    Favorites
                </Button>
                <Button
                    size="xs"
                    radius="xl"
                    variant={unwatchedOnly ? 'filled' : 'default'}
                    onClick={() =>
                        set('user_has_watched', unwatchedOnly ? null : 'false')
                    }
                >
                    Unwatched
                </Button>
                <Divider orientation="vertical" h={20} my="auto" />
                <GenreFilter
                    type="series"
                    selectedIds={genreIds}
                    onSelected={setGenres}
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
