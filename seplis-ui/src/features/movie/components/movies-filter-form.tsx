import { DateishInput } from '@/components/dateish-input'
import { TristateCheckbox } from '@/components/tristate-checkbox'
import { Flex, Select, Text } from '@mantine/core'
import { MoviesGetParams } from '../types/movies.types'

interface Props {
    filter: MoviesGetParams
    setFilter: (filter: MoviesGetParams) => void
}

export function MoviesFilterForm({ filter, setFilter }: Props) {
    return (
        <Flex gap="1rem" direction="column">
            <Flex gap="0.5rem" direction="column">
                <TristateCheckbox
                    checked={filter.user_can_watch}
                    onCheckedChanged={(e) =>
                        setFilter({
                            ...filter,
                            user_can_watch: e,
                        })
                    }
                    label="Available to Watch"
                />
                <TristateCheckbox
                    checked={filter.user_watchlist}
                    onCheckedChanged={(e) =>
                        setFilter({
                            ...filter,
                            user_watchlist: e,
                        })
                    }
                    label="Watchlist"
                />
                <TristateCheckbox
                    checked={filter.user_favorites}
                    onCheckedChanged={(e) =>
                        setFilter({
                            ...filter,
                            user_favorites: e,
                        })
                    }
                    label="Favorites"
                />
                <TristateCheckbox
                    checked={filter.user_has_watched}
                    onCheckedChanged={(e) =>
                        setFilter({
                            ...filter,
                            user_has_watched: e,
                        })
                    }
                    label="Watched"
                />
            </Flex>

            <Flex gap="0.5rem" direction="column">
                <Flex direction="column" gap="0.15rem">
                    <Text size="sm" fw={600}>
                        Released After
                    </Text>
                    <DateishInput
                        defaultValue={filter.release_date_gt ?? ''}
                        onChange={(v) =>
                            setFilter({
                                ...filter,
                                release_date_gt: v || undefined,
                            })
                        }
                    />
                </Flex>
                <Flex direction="column" gap="0.15rem">
                    <Text size="sm" fw={600}>
                        Released Before
                    </Text>
                    <DateishInput
                        defaultValue={filter.release_date_lt ?? ''}
                        onChange={(v) =>
                            setFilter({
                                ...filter,
                                release_date_lt: v || undefined,
                            })
                        }
                    />
                </Flex>
            </Flex>

            <Flex gap="0.5rem" direction="column">
                <Flex direction="column" gap="0.15rem">
                    <Text size="sm" fw={600}>
                        Rating
                    </Text>
                    <Flex gap="0.5rem" align="center">
                        <Select
                            w={100}
                            value={filter.rating_gt ?? ''}
                            data={Array.from({ length: 10 }, (_, i) => ({
                                value: i,
                                label: String(i + 1),
                            })).reverse()}
                            onChange={(e) =>
                                setFilter({
                                    ...filter,
                                    rating_gt: e || undefined,
                                })
                            }
                            clearable
                        />
                        <Text size="sm">to</Text>
                        <Select
                            w={100}
                            value={filter.rating_lt ?? ''}
                            data={Array.from({ length: 10 }, (_, i) => ({
                                value: i + 1,
                                label: String(i + 1),
                            })).reverse()}
                            onChange={(e) =>
                                setFilter({
                                    ...filter,
                                    rating_lt: e || undefined,
                                })
                            }
                            clearable
                        />
                    </Flex>
                </Flex>
            </Flex>
        </Flex>
    )
}
