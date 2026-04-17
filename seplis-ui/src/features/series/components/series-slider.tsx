import { PosterImage } from '@/components/poster-image/poster-image'
import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
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
            startPadding="0.5rem"
            renderItem={(item) => (
                <PosterImage
                    posterImage={item.poster_image}
                    title={item.title}
                />
            )}
            renderHoverCard={(item) => <SeriesHoverCard series={item} />}
        />
    )
}
