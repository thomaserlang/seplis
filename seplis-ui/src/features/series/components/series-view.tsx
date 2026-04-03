import { Series } from '../types/series.types'
import { SeriesEpisodes } from './series-episodes'
import { SeriesInfo } from './series-info'

interface Props {
    series: Series
}

export function SeriesView({ series }: Props) {
    return (
        <div>
            <SeriesInfo series={series} />
            {series.seasons.length > 0 && <SeriesEpisodes series={series} />}
        </div>
    )
}
