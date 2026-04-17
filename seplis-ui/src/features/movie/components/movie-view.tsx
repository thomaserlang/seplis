import { Flex, Text } from '@mantine/core'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Movie } from '../types/movie.types'
import { MovieCastModal } from './movie-cast-modal'
import { MovieCastSlider } from './movie-cast-slider'
import { MovieInfo } from './movie-info'
import { MoviesSlider } from './movies-slider'

interface Props {
    movie: Movie
}

export function MovieView({ movie }: Props) {
    const [modal, setModal] = useState<'cast' | undefined>(undefined)
    const [_, setParams] = useSearchParams()

    return (
        <>
            <Flex direction="column">
                <title>{movie.title}</title>
                <MovieInfo movie={movie}>
                    <MovieCastSlider
                        movieId={movie.id}
                        maxCast={22}
                        background="var(--card)"
                        title={
                            <Text
                                onClick={() => setModal('cast')}
                                size="md"
                                fw="700"
                                style={{ cursor: 'pointer' }}
                            >
                                Top Cast
                            </Text>
                        }
                        onClick={() => setModal('cast')}
                    />
                    {movie.collection?.id && (
                        <MoviesSlider
                            title={movie.collection.name}
                            background="var(--card)"
                            itemWidth="7.5rem"
                            startPadding="0"
                            params={{
                                collection_id: [movie.collection.id],
                                sort: ['release_date_asc'],
                            }}
                            onClick={(movie) =>
                                setParams({ mid: `movie-${movie.id}` })
                            }
                        />
                    )}
                </MovieInfo>
            </Flex>

            <MovieCastModal
                movieId={movie.id}
                opened={modal === 'cast'}
                onClose={() => setModal(undefined)}
            />
        </>
    )
}
