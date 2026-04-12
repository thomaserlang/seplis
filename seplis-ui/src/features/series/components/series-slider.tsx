import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Image } from '@mantine/core'
import { useGetSeriesList } from '../api/series-list.api'
import { SeriesListGetParams } from '../types/series-list.types'
import { Series } from '../types/series.types'
import { SeriesHoverCard } from './series-hover-card'

interface Props {
    onClick: (series: Series) => void
    params: SeriesListGetParams
    title?: string
}

export function SeriesSlider({ onClick, params, title }: Props) {
    const { data, isLoading, fetchNextPage } = useGetSeriesList({
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
                    src={`${item.poster_image?.url}@SX320.webp`}
                    radius="sm"
                />
            )}
            renderHoverCard={(item) => <SeriesHoverCard series={item} />}
        />
    )
}
