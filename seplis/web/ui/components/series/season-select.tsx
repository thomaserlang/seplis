import { Select } from '@chakra-ui/react'
import { ISeriesSeason } from '@seplis/interfaces/series'

interface IProps {
    seasons: ISeriesSeason[]
    onSelect?: (season: number) => void,
    defaultSeason?: number
}

export default function SeasonSelect({ seasons, onSelect, defaultSeason=1 }: IProps) {
    return <Select defaultValue={defaultSeason} onChange={(value) => {
        if (onSelect)
            onSelect(parseInt(value.currentTarget.value))
    }}>
        {seasons.map(season => (
            <option key={season.season} value={season.season}>Season {season.season}</option>
        ))}
    </Select>
}