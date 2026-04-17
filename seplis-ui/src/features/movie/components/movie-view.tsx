import { Button, Flex, Text } from '@mantine/core'
import { UsersIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import { Movie } from '../types/movie.types'
import { MovieCast } from './movie-cast'
import { MovieCastModal } from './movie-cast-modal'
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
                    <Flex gap="0.5rem">
                        <Button
                            variant="default"
                            leftSection={<UsersIcon />}
                            onClick={() => setModal('cast')}
                        >
                            Cast
                        </Button>
                    </Flex>
                </MovieInfo>

                <Flex gap="0.5rem" p="1rem" pt="0.5rem" direction="column">
                    <MovieCast
                        movieId={movie.id}
                        maxCast={14}
                        title={
                            <Text size="md" fw="700" mb="0.4rem">
                                Top Cast
                            </Text>
                        }
                    />
                </Flex>
            </Flex>
            <MovieCastModal
                movieId={movie.id}
                opened={modal === 'cast'}
                onClose={() => setModal(undefined)}
            />
        </>
    )
}
