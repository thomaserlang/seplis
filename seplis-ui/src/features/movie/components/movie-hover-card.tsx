import { MediaInfoHoverCard } from '@/components/media-info'
import { mediaTypes } from '@/features/media-type'
import { Flex } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'
import { Movie } from '../types/movie.types'
import { MovieFavoriteButton } from './movie-favorite-button'
import { MovieMetaItems } from './movie-info'
import { MoviePlayButton } from './movie-play-button'
import { MovieWatchedButton } from './movie-watched-button'
import { MovieWatchlistButton } from './movie-watchlist-button'

interface Props {
    movie: Movie
}

export function MovieHoverCard({ movie }: Props) {
    const [_, setParams] = useSearchParams()

    const handleClick = () => {
        setParams((params) => {
            params.set('mid', `movie-${movie.id}`)
            return params
        })
    }
    return (
        <MediaInfoHoverCard
            posterUrl={movie.poster_image?.url}
            title={movie.title || movie.original_title || 'Untitled'}
            accentHue={mediaTypes['movie'].accentHue}
            metaItems={MovieMetaItems({
                movie,
                showReleaseDate: true,
                showRuntime: true,
                showLanguage: true,
                showRating: true,
            })}
            genres={movie.genres}
            onInfoClick={handleClick}
        >
            <Flex gap="0.5rem" wrap="wrap">
                <MoviePlayButton movieId={movie.id} size="compact-sm" />
                <MovieWatchedButton
                    movieId={movie.id}
                    duration={movie.runtime}
                    size="compact-sm"
                />
                <MovieWatchlistButton movieId={movie.id} size="compact-sm" />
                <MovieFavoriteButton movieId={movie.id} size="compact-sm" />
            </Flex>
        </MediaInfoHoverCard>
    )
}
