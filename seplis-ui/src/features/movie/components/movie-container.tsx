import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Flex } from '@mantine/core'
import { useGetMovie } from '../api/movie.api'
import { MovieView } from './movie-view'

interface Props {
    movieId: number
}

export function MovieContainer({ movieId }: Props) {
    const { data, isLoading, error } = useGetMovie({
        movieId,
    })

    return (
        <>
            {isLoading && (
                <Flex
                    justify="center"
                    align="center"
                    style={{ height: '50dvh' }}
                >
                    <PageLoader />
                </Flex>
            )}
            {error && !data && <ErrorBox errorObj={error} />}
            {data && <MovieView movie={data} />}
        </>
    )
}
