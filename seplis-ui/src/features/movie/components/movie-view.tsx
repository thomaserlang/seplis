import { Flex, Text } from '@mantine/core'
import { useState } from 'react'
import { Movie } from '../types/movie.types'
import { MovieCastModal } from './movie-cast-modal'
import { MovieCastSlider } from './movie-cast-slider'
import { MovieInfo } from './movie-info'

interface Props {
    movie: Movie
}

export function MovieView({ movie }: Props) {
    const [modal, setModal] = useState<'cast' | undefined>(undefined)

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
