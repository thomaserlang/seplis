import { GenreSelect } from '@/components/genre-select'
import { LanguageSelect } from '@/components/language-select'
import classes from '@/components/poster-page/poster-page.module.css'
import { isEmpty } from '@/utils/str.utils'
import {
    Button,
    ButtonProps,
    Divider,
    Drawer,
    ScrollArea,
    Select,
} from '@mantine/core'
import { useState } from 'react'
import { MOVIE_SORT_OPTIONS, MoviesGetParams } from '../types/movies.types'
import { MoviesFilterForm } from './movies-filter-form'

interface Props {
    filter: MoviesGetParams
    setFilter: (filter: MoviesGetParams) => void
}

export function MoviesFilterbar({ filter, setFilter }: Props) {
    const [showFilter, setShowFilter] = useState(false)

    return (
        <>
            <div className={classes.filterBar}>
                <Select
                    size="xs"
                    value={filter.sort?.[0] ?? 'popularity_desc'}
                    onChange={(v) =>
                        setFilter({ ...filter, sort: v ? [v] : undefined })
                    }
                    data={MOVIE_SORT_OPTIONS}
                    w={160}
                    allowDeselect={false}
                    radius="xl"
                />

                <Divider orientation="vertical" h={20} my="auto" />

                <FilterButton
                    active={filter.user_can_watch === true}
                    onClick={() =>
                        setFilter({
                            ...filter,
                            user_can_watch: filter.user_can_watch
                                ? undefined
                                : true,
                        })
                    }
                >
                    Available
                </FilterButton>
                <FilterButton
                    active={filter.user_watchlist === true}
                    onClick={() =>
                        setFilter({
                            ...filter,
                            user_watchlist: filter.user_watchlist
                                ? undefined
                                : true,
                        })
                    }
                >
                    Watchlist
                </FilterButton>
                <FilterButton
                    active={filter.user_favorites === true}
                    onClick={() =>
                        setFilter({
                            ...filter,
                            user_favorites: filter.user_favorites
                                ? undefined
                                : true,
                        })
                    }
                >
                    Favorites
                </FilterButton>
                <FilterButton
                    active={filter.user_has_watched === false}
                    onClick={() =>
                        setFilter({
                            ...filter,
                            user_has_watched:
                                filter.user_has_watched === false
                                    ? undefined
                                    : false,
                        })
                    }
                >
                    Unwatched
                </FilterButton>

                <Divider orientation="vertical" h={20} my="auto" />

                <GenreSelect
                    type="movie"
                    selectedIds={filter.genre_id ?? []}
                    onSelected={(ids) =>
                        setFilter({
                            ...filter,
                            genre_id: ids.length ? ids : undefined,
                        })
                    }
                >
                    <FilterButton active={!isEmpty(filter.genre_id)}>
                        {!isEmpty(filter.genre_id)
                            ? `Genres (${filter.genre_id.length})`
                            : 'Genres'}
                    </FilterButton>
                </GenreSelect>
                <LanguageSelect
                    selected={filter.language ?? []}
                    onChange={(langs) =>
                        setFilter({
                            ...filter,
                            language: langs.length ? langs : undefined,
                        })
                    }
                >
                    <FilterButton active={!isEmpty(filter.language)}>
                        {!isEmpty(filter.language)
                            ? `Languages (${filter.language.length})`
                            : 'Languages'}
                    </FilterButton>
                </LanguageSelect>

                <Divider orientation="vertical" h={20} my="auto" />

                <FilterButton onClick={() => setShowFilter(!showFilter)}>
                    Advanced
                </FilterButton>
            </div>
            <Drawer
                opened={showFilter}
                onClose={() => setShowFilter(false)}
                title="Advanced Filters"
                position="right"
                scrollAreaComponent={ScrollArea.Autosize}
            >
                <MoviesFilterForm filter={filter} setFilter={setFilter} />
            </Drawer>
        </>
    )
}

function FilterButton({
    active,
    ...props
}: ButtonProps & { active?: boolean; onClick?: () => void }) {
    return (
        <Button
            size="xs"
            radius="xl"
            variant={active ? 'filled' : 'default'}
            {...props}
        />
    )
}
