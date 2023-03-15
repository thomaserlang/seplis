import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { isAuthed } from '@seplis/utils'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'
import { ISeriesFavorite } from '@seplis/interfaces/series'
import { StarIcon } from '@chakra-ui/icons'


export default function FavoriteButton({ seriesId }: { seriesId: number }) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleFavorite = useMutation(async (favorite: boolean) => {
        await queryClient.cancelQueries(['series', 'favorite-button', seriesId])
        if (favorite) {
            await api.delete(`/2/series/${seriesId}/favorite`)
        } else {
            await api.put(`/2/series/${seriesId}/favorite`)
        }
        queryClient.setQueryData(['series', 'favorite-button', seriesId], { favorite: !favorite })
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

    const { isInitialLoading, data } = useQuery(['series', 'favorite-button', seriesId], async () => {
        const result = await api.get<ISeriesFavorite>(`/2/series/${seriesId}/favorite`)
        return result.data
    }, {
        enabled: isAuthed()
    })

    const handleClick = () => {
        toggleFavorite.mutate(data.favorite)
    }

    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick,
    })

    return <Button
        ref={ref}
        isLoading={isInitialLoading || toggleFavorite.isLoading}
        colorScheme={data?.favorite ? 'blue' : null}
        onClick={handleClick}
        leftIcon={<StarIcon />}
        style={focused ? focusedBorder : null}
    >
        Favorite
    </Button>
}