import { PlayButton, PlayButtonProps } from '@/features/play'
import { useActiveUser } from '@/features/user'
import { useSearchParams } from 'react-router-dom'
import { useGetMoviePlayRequests } from '../api/movie-play-requests.api'

interface Props extends Partial<PlayButtonProps> {
    movieId: number
}

export function MoviePlayButton({ movieId, ...props }: Props) {
    const [_, setParams] = useSearchParams()
    const [user] = useActiveUser()
    const { data, isLoading, refetch } = useGetMoviePlayRequests({
        movieId,
        options: {
            enabled: !!user,
        },
    })
    return (
        <PlayButton
            playRequests={data ?? []}
            getPlayRequests={refetch}
            loading={isLoading}
            disabled={!data || data.length === 0}
            onClick={() => {
                setParams((params) => {
                    params.set('pid', `movie-${movieId}`)
                    return params
                })
            }}
            {...props}
        />
    )
}
