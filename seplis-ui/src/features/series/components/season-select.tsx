import { Select } from '@mantine/core'
import { SeriesSeason } from '../types/series.types'

interface Props extends React.ComponentPropsWithoutRef<typeof Select> {
    seasons: SeriesSeason[]
}

export function SeasonSelect({ seasons, ...props }: Props) {
    const seasonOptions = seasons.map((s) => ({
        value: s.season,
        label: `Season ${s.season}`,
    }))

    return (
        <Select
            data={seasonOptions}
            size="xs"
            w={120}
            allowDeselect={false}
            {...props}
        />
    )
}
