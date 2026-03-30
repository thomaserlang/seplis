import api from '@/api'
import { IMovieFavorite } from '@/interfaces/movie'
import { focusedBorder } from '@/styles'
import { isAuthed } from '@/utils'
import { StarIcon } from '@chakra-ui/icons'
import { Button, useToast } from '@chakra-ui/react'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorMessageFromResponse } from '../error'

interface IProps {
    movieId: number
}

export default function WatchlistButton({ movieId }: IProps) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleWatchlist = useMutation(
        async (favorite: boolean) => {
            await queryClient.cancelQueries([
                'movie',
                'favorite-button',
                movieId,
            ])
            if (favorite) {
                await api.delete(`/2/movies/${movieId}/favorite`)
            } else {
                await api.put(`/2/movies/${movieId}/favorite`)
            }
            queryClient.setQueryData(['movie', 'favorite-button', movieId], {
                favorite: !favorite,
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

    const { isInitialLoading, data } = useQuery(
        ['movie', 'favorite-button', movieId],
        async () => {
            const result = await api.get<IMovieFavorite>(
                `/2/movies/${movieId}/favorite`,
            )
            return result.data
        },
        {
            enabled: isAuthed(),
        },
    )
    const handleClick = async () => {
        toggleWatchlist.mutate(data?.favorite ?? false)
    }
    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick(),
    })

    return (
        <Button
            ref={ref}
            isLoading={isInitialLoading || toggleWatchlist.isLoading}
            colorScheme={data?.favorite ? 'blue' : undefined}
            onClick={handleClick}
            leftIcon={<StarIcon />}
            style={focused ? focusedBorder : undefined}
        >
            Favorite
        </Button>
    )
}
