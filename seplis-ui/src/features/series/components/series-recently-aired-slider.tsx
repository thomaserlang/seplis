import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Image } from '@mantine/core'
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
        params,
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
                <Image
                    src={`${item.series.poster_image?.url}@SX320.webp`}
                    radius="sm"
                />
            )}
            renderHoverCard={(item) => <SeriesHoverCard series={item.series} />}
        />
    )
}
