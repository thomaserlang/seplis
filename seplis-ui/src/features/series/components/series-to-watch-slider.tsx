import { PosterImage } from '@/components/poster-image/poster-image'
import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { useGetSeriesToWatch } from '../api/series-to-watch.api'
import { SeriesListGetParams } from '../types/series-list.types'
import { SeriesAndEpisode } from '../types/series.types'
import { SeriesHoverCard } from './series-hover-card'

interface Props {
    onClick: (series: SeriesAndEpisode) => void
    params: SeriesListGetParams
    title?: string
}

export function SeriesToWatchSlider({ onClick, params, title }: Props) {
    const { data, isLoading, fetchNextPage } = useGetSeriesToWatch({
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
                <PosterImage
                    posterImage={item.series.poster_image}
                    title={item.series.title}
                />
            )}
            renderHoverCard={(item) => <SeriesHoverCard series={item.series} />}
        />
    )
}
