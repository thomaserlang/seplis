import { PosterImage } from '@/components/poster-image'
import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { ReactNode } from 'react'
import { useGetSeriesCast } from '../api/series-cast.api'

interface Props {
    seriesId: number
    maxCast?: number
    title?: ReactNode
    background?: string
    onClick?: () => void
}

export function SeriesCastSlider({
    seriesId,
    maxCast,
    title,
    onClick,
    background,
}: Props) {
    const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
        useGetSeriesCast({
            seriesId,
            params: {
                order_le: maxCast ? 99 : undefined,
                per_page: maxCast ? Math.min(maxCast, 100) : 25,
            },
        })

    const cast = pageItemsFlatten(data)
    const items = maxCast ? cast.slice(0, maxCast) : cast

    return (
        <Slider
            title={title}
            items={items}
            isLoading={isLoading || isFetchingNextPage}
            onLoadMore={!maxCast && hasNextPage ? fetchNextPage : undefined}
            itemWidth="min(5rem, 30vw)"
            skeletonCount={maxCast ? Math.min(maxCast, 8) : 8}
            onClick={onClick}
            background={background}
            renderItem={(item) => (
                <PosterImage
                    posterImage={item.person.profile_image}
                    title={item.person.name}
                    sizeX={180}
                />
            )}
        />
    )
}
