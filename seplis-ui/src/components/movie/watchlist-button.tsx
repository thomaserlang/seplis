import api from '@/api'
import { EVENT_MOVIE_WATCHED, useEventListener } from '@/events'
import { IEventMovieWatched, IMovieWatchlist } from '@/interfaces/movie'
import { focusedBorder } from '@/styles'
import { isAuthed } from '@/utils'
import { Button, useToast } from '@chakra-ui/react'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FaBookmark } from 'react-icons/fa'
import { ErrorMessageFromResponse } from '../error'

interface IProps {
    movieId: number
}

export default function WatchlistButton({ movieId }: IProps) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleWatchlist = useMutation(
        async (onWatchlist: boolean) => {
            await queryClient.cancelQueries([
                'movie',
                'watchlist-button',
                movieId,
            ])
            if (onWatchlist) {
                await api.delete(`/2/movies/${movieId}/watchlist`)
            } else {
                await api.put(`/2/movies/${movieId}/watchlist`)
            }
            queryClient.setQueryData(['movie', 'watchlist-button', movieId], {
                on_watchlist: !onWatchlist,
            })
        },
        {
            onError: (e) => {
                toast({
                    title: ErrorMessageFromResponse(e),
                    status: 'error',
                    isClosable: true,
                    position: 'top',
                })
            },
        },
    )

    useEventListener<IEventMovieWatched>(
        EVENT_MOVIE_WATCHED,
        (data) => {
            if (data.movieId == movieId)
                queryClient.setQueryData(
                    ['movie', 'watchlist-button', movieId],
                    { on_watchlist: false },
                )
        },
        [movieId],
    )

    const { isInitialLoading, data } = useQuery(
        ['movie', 'watchlist-button', movieId],
        async () => {
            const result = await api.get<IMovieWatchlist>(
                `/2/movies/${movieId}/watchlist`,
            )
            return result.data
        },
        {
            enabled: isAuthed(),
        },
    )
    const handleClick = async () => {
        toggleWatchlist.mutate(data?.on_watchlist ?? false)
    }
    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick(),
    })

    return (
        <Button
            ref={ref}
            isLoading={isInitialLoading || toggleWatchlist.isLoading}
            colorScheme={data?.on_watchlist ? 'yellow' : undefined}
            onClick={handleClick}
            leftIcon={<FaBookmark />}
            style={focused ? focusedBorder : undefined}
        >
            Watchlist
        </Button>
    )
}
