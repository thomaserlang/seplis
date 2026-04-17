import { PosterImage } from '@/components/poster-image/poster-image'
import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { useGetMovies } from '../api/movies.api'
import { Movie } from '../types/movie.types'
import { MoviesGetParams } from '../types/movies.types'
import { MovieHoverCard } from './movie-hover-card'

interface Props {
    onClick: (movie: Movie) => void
    params: MoviesGetParams
    title?: string
    itemWidth?: string
    startPadding?: string
    background?: string
}

export function MoviesSlider({
    onClick,
    params,
    title,
    itemWidth,
    startPadding = '0.5rem',
    background,
}: Props) {
    const { data, isLoading, fetchNextPage } = useGetMovies({
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
            itemWidth={itemWidth}
            startPadding={startPadding}
            background={background}
            renderItem={(item) => (
                <PosterImage
                    posterImage={item.poster_image}
                    title={item.title}
                />
            )}
            renderHoverCard={(item) => <MovieHoverCard movie={item} />}
        />
    )
}
