import { PosterImage } from '@/components/poster-image/poster-image'
import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import {
    SeriesRecentlyAiredGetParams,
    useGetSeriesRecentlyAired,
} from '../api/series-recently-aired.api'
import { SeriesAndEpisode } from '../types/series.types'
import { SeriesHoverCard } from './series-hover-card'

interface Props {
    onClick: (series: SeriesAndEpisode) => void
    params: SeriesRecentlyAiredGetParams
    title?: string
}

export function SeriesRecentlyAiredSlider({ onClick, params, title }: Props) {
    const { data, isLoading, fetchNextPage } = useGetSeriesRecentlyAired({
        params: {
            ...params,
            per_page: 24,
        },
    })
    const items = pageItemsFlatten(data)

    return (
        <Slider
            title={title}
            items={items}
            isLoading={isLoading}
            onLoadMore={fetchNextPage}
            onClick={onClick}
            renderItem={(item) => (
                <PosterImage
                    posterImage={item.series.poster_image}
                    title={item.series.title}
                />
            )}
            renderHoverCard={(item) => <SeriesHoverCard series={item.series} />}
        />
    )
}
