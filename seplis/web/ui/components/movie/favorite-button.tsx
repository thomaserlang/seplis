import { StarIcon } from '@chakra-ui/icons'
import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovieFavorite, IMovieWatchlist } from '@seplis/interfaces/movie'
import { isAuthed } from '@seplis/utils'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'

interface IProps {
    movieId: number
}

export default function WatchlistButton({ movieId }: IProps) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleWatchlist = useMutation(async (favorite: boolean) => {
        await queryClient.cancelQueries(['movie', 'favorite-button', movieId])
        let data: IMovieWatchlist
        if (favorite) {
            data = await api.delete(`/2/movies/${movieId}/favorite`)
        } else {
            data = await api.put(`/2/movies/${movieId}/favorite`)
        }
        queryClient.setQueryData(['movie', 'favorite-button', movieId], { favorite: !favorite })
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

    const { isInitialLoading, data } = useQuery(['movie', 'favorite-button', movieId], async () => {
        const result = await api.get<IMovieFavorite>(`/2/movies/${movieId}/favorite`)
        return result.data
    }, {
        enabled: isAuthed(),
    })
    const handleClick = async () => {
        toggleWatchlist.mutate(data.favorite)
    }
    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick()
    })

    return <Button
        ref={ref}
        isLoading={isInitialLoading || toggleWatchlist.isLoading}
        colorScheme={data?.favorite ? 'blue' : null}
        onClick={handleClick}
        leftIcon={<StarIcon />}
        style={focused ? focusedBorder : null}
    >
        Favorite
    </Button>
}