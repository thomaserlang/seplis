import { PosterImage } from '@/components/poster-image'
import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { ReactNode } from 'react'
import { useGetMovieCast } from '../api/movie-cast.api'

interface Props {
    movieId: number
    maxCast?: number
    title?: ReactNode
    background?: string
    startPadding?: string
    onClick?: () => void
}

export function MovieCastSlider({
    movieId,
    maxCast,
    title,
    onClick,
    background,
    startPadding,
}: Props) {
    const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
        useGetMovieCast({
            movieId,
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
            startPadding={startPadding}
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
