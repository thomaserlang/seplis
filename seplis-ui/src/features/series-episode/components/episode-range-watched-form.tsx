import { Button, Flex, Select } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useEffect } from 'react'
import { useSetEpisodeRangeWatched } from '../api/episode-range-watched.api'
import { SeriesSeason } from '../types/series-season.types'
import { SeasonSelect } from './season-select'

interface FormValues {
    fromSeason: string
    fromEpisode: string
    toSeason: string
    toEpisode: string
}

interface Props {
    onClose: () => void
    seriesId: number
    season: number
    seasons: SeriesSeason[]
}

export function EpisodeRangeWatchedForm({
    onClose,
    seriesId,
    season,
    seasons,
}: Props) {
    const currentSeason =
        seasons.find((seasonInfo) => seasonInfo.season === season) ?? seasons[0]
    const hasEpisodes = seasons.some((seasonInfo) => seasonInfo.total > 0)

    const form = useForm<FormValues>({
        initialValues: createInitialValues(currentSeason),
        validate: {
            fromEpisode: (_, values) => {
                if (!hasEpisodes) return 'No episodes available in this series'

                const absoluteFrom = toAbsoluteEpisodeNumber(
                    seasons,
                    values.fromSeason,
                    values.fromEpisode,
                )
                const absoluteTo = toAbsoluteEpisodeNumber(
                    seasons,
                    values.toSeason,
                    values.toEpisode,
                )

                if (absoluteFrom == null) return 'Select a valid start episode'
                if (absoluteTo == null) return null
                if (absoluteFrom > absoluteTo) {
                    return 'Start episode must be before or equal to end episode'
                }
                return null
            },
            toEpisode: (_, values) => {
                if (!hasEpisodes) return 'No episodes available in this series'

                const absoluteFrom = toAbsoluteEpisodeNumber(
                    seasons,
                    values.fromSeason,
                    values.fromEpisode,
                )
                const absoluteTo = toAbsoluteEpisodeNumber(
                    seasons,
                    values.toSeason,
                    values.toEpisode,
                )

                if (absoluteTo == null) return 'Select a valid end episode'
                if (absoluteFrom == null) return null
                if (absoluteTo < absoluteFrom) {
                    return 'End episode must be after or equal to start episode'
                }
                return null
            },
        },
    })

    useEffect(() => {
        const initialValues = createInitialValues(currentSeason)
        form.setValues(initialValues)
        form.resetDirty()
        form.clearErrors()
    }, [currentSeason?.season, currentSeason?.total])

    const setRangeWatched = useSetEpisodeRangeWatched({
        onSuccess: () => {
            onClose()
        },
    })

    const fromSeason = getSeasonByValue(seasons, form.values.fromSeason)
    const toSeason = getSeasonByValue(seasons, form.values.toSeason)

    return (
        <form
            onSubmit={form.onSubmit((values) => {
                const fromEpisodeNumber = toAbsoluteEpisodeNumber(
                    seasons,
                    values.fromSeason,
                    values.fromEpisode,
                )
                const toEpisodeNumber = toAbsoluteEpisodeNumber(
                    seasons,
                    values.toSeason,
                    values.toEpisode,
                )

                if (fromEpisodeNumber == null || toEpisodeNumber == null) return

                setRangeWatched.mutate({
                    seriesId,
                    data: {
                        from_episode_number: fromEpisodeNumber,
                        to_episode_number: toEpisodeNumber,
                    },
                })
            })}
        >
            <Flex direction="column" gap="md">
                <Flex gap="sm" align="flex-end" wrap="nowrap">
                    <SeasonSelect
                        seasons={seasons}
                        label="From"
                        value={form.values.fromSeason}
                        size="sm"
                        flex={1}
                        w="auto"
                        disabled={!hasEpisodes}
                        onChange={(value) => {
                            const nextValue = normalizeSelectValue(value)
                            const nextSeason = getSeasonByValue(
                                seasons,
                                nextValue,
                            )
                            form.setFieldValue('fromSeason', nextValue)
                            form.setFieldValue(
                                'fromEpisode',
                                getClampedEpisodeValue(
                                    nextSeason,
                                    form.values.fromEpisode,
                                ),
                            )
                        }}
                    />

                    <Select
                        data={getEpisodeOptions(fromSeason)}
                        value={form.values.fromEpisode}
                        allowDeselect={false}
                        size="sm"
                        flex={1}
                        disabled={!fromSeason}
                        onChange={(value) =>
                            form.setFieldValue('fromEpisode', value ?? '')
                        }
                    />
                </Flex>

                <Flex gap="sm" align="flex-end" wrap="nowrap">
                    <SeasonSelect
                        seasons={seasons}
                        label="To"
                        value={form.values.toSeason}
                        size="sm"
                        flex={1}
                        w="auto"
                        disabled={!hasEpisodes}
                        onChange={(value) => {
                            const nextValue = normalizeSelectValue(value)
                            const nextSeason = getSeasonByValue(
                                seasons,
                                nextValue,
                            )
                            form.setFieldValue('toSeason', nextValue)
                            form.setFieldValue(
                                'toEpisode',
                                getClampedEpisodeValue(
                                    nextSeason,
                                    form.values.toEpisode,
                                ),
                            )
                        }}
                    />

                    <Select
                        data={getEpisodeOptions(toSeason)}
                        value={form.values.toEpisode}
                        allowDeselect={false}
                        size="sm"
                        flex={1}
                        disabled={!toSeason}
                        error={form.errors.toEpisode || form.errors.fromEpisode}
                        onChange={(value) =>
                            form.setFieldValue('toEpisode', value ?? '')
                        }
                    />
                </Flex>

                <Flex justify="flex-end" gap="sm">
                    <Button variant="default" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        loading={setRangeWatched.isPending}
                        disabled={!hasEpisodes}
                    >
                        Mark watched
                    </Button>
                </Flex>
            </Flex>
        </form>
    )
}

function createInitialValues(currentSeason?: SeriesSeason): FormValues {
    return {
        fromSeason: currentSeason ? String(currentSeason.season) : '',
        fromEpisode: '1',
        toSeason: currentSeason ? String(currentSeason.season) : '',
        toEpisode: currentSeason ? String(currentSeason.total) : '',
    }
}

function getSeasonByValue(
    seasons: SeriesSeason[],
    value: string | null | undefined,
) {
    return seasons.find((season) => String(season.season) === value)
}

function getEpisodeOptions(season?: SeriesSeason) {
    if (!season) return []

    return Array.from({ length: season.total }, (_, index) => {
        const episode = index + 1
        return {
            value: String(episode),
            label: `Episode ${episode}`,
        }
    })
}

function getClampedEpisodeValue(
    season: SeriesSeason | undefined,
    episodeValue: string,
) {
    if (!season) return ''

    const parsedEpisode = Number(episodeValue)
    if (!Number.isFinite(parsedEpisode) || parsedEpisode < 1) return '1'
    return String(Math.min(parsedEpisode, season.total))
}

function toAbsoluteEpisodeNumber(
    seasons: SeriesSeason[],
    seasonValue: string,
    episodeValue: string,
) {
    const season = getSeasonByValue(seasons, seasonValue)
    const localEpisode = Number(episodeValue)

    if (!season || !Number.isInteger(localEpisode)) return null
    if (localEpisode < 1 || localEpisode > season.total) return null

    return season.from + localEpisode - 1
}

function normalizeSelectValue(
    value: string | number | bigint | boolean | null,
) {
    return value == null ? '' : String(value)
}
