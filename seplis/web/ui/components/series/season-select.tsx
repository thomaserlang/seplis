import { Select } from '@chakra-ui/react'
import { ISeriesSeason } from '@seplis/interfaces/series'

interface IProps {
    seasons: ISeriesSeason[]
    onSelect?: (season: number) => void,
    season: number
}

export default function SeasonSelect({ seasons, onSelect, season }: IProps) {
    if (!seasons || (seasons.length == 0))
        return null
    return <Select value={season} onChange={(value) => {
        if (onSelect)
            onSelect(parseInt(value.currentTarget.value))
    }}>
        {seasons.map(season => (
            <option key={season.season} value={season.season}>Season {season.season}</option>
        ))}
    </Select>
}