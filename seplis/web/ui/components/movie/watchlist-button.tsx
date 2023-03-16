import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IEventMovieWatched, IMovieWatchlist } from '@seplis/interfaces/movie'
import { isAuthed } from '@seplis/utils'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'
import { FaBookmark } from 'react-icons/fa'
import { EVENT_MOVIE_WATCHED, useEventListener } from '@seplis/events'

interface IProps {
    movieId: number
}

export default function WatchlistButton({ movieId }: IProps) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleWatchlist = useMutation(async (onWatchlist: boolean) => {
        await queryClient.cancelQueries(['movie', 'watchlist-button', movieId])
        let data: IMovieWatchlist
        if (onWatchlist) {
            data = await api.delete(`/2/movies/${movieId}/watchlist`)
        } else {
            data = await api.put(`/2/movies/${movieId}/watchlist`)
        }
        queryClient.setQueryData(['movie', 'watchlist-button', movieId], { on_watchlist: !onWatchlist })
    }, {
        onError: (e) => {
            toast({
                title: ErrorMessageFromResponse(e),
                status: 'error',
                isClosable: true,
                position: 'top',
            })
        }
    })

    useEventListener<IEventMovieWatched>(EVENT_MOVIE_WATCHED, ((data) => {
        if (data.movieId == movieId)
            queryClient.setQueryData(['movie', 'watchlist-button', movieId], { on_watchlist: false })
    }), [movieId])

    const { isInitialLoading, data } = useQuery(['movie', 'watchlist-button', movieId], async () => {
        const result = await api.get<IMovieWatchlist>(`/2/movies/${movieId}/watchlist`)
        return result.data
    }, {
        enabled: isAuthed(),
    })
    const handleClick = async () => {
        toggleWatchlist.mutate(data.on_watchlist)
    }
    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick()
    })

    return <Button
        ref={ref}
        isLoading={isInitialLoading || toggleWatchlist.isLoading}
        colorScheme={data?.on_watchlist ? 'yellow' : null}
        onClick={handleClick}
        leftIcon={<FaBookmark />}
        style={focused ? focusedBorder : null}
    >
        Watchlist
    </Button>
}