import { Slider } from '@/components/slider'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Image } from '@mantine/core'
import { useGetMovies } from '../api/movies.api'
import { Movie } from '../types/movie.types'
import { MoviesGetParams } from '../types/movies.types'
import { MovieHoverCard } from './movie-hover-card'

interface Props {
    onClick: (movie: Movie) => void
    params: MoviesGetParams
    title?: string
}

export function MoviesSlider({ onClick, params, title }: Props) {
    const { data, isLoading, fetchNextPage } = useGetMovies({
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
            renderHoverCard={(item) => <MovieHoverCard movie={item} />}
        />
    )
}
