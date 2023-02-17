import { StarIcon } from '@chakra-ui/icons'
import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovieStared } from '@seplis/interfaces/movie'
import { isAuthed } from '@seplis/utils'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'

interface IProps {
    movieId: number
}

export default function StaredButton({ movieId }: IProps) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleStared = useMutation(async (stared: boolean) => {
        await queryClient.cancelQueries(['movie', 'stared-button', movieId])
        let data: IMovieStared
        if (stared) {
            data = await api.delete(`/2/movies/${movieId}/stared`)
        } else {
            data = await api.put(`/2/movies/${movieId}/stared`)
        }
        queryClient.setQueryData(['movie', 'stared-button', movieId], { stared: !stared })
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

    const { isInitialLoading, data } = useQuery(['movie', 'stared-button', movieId], async () => {
        if (!isAuthed())
            return
        const result = await api.get<IMovieStared>(`/2/movies/${movieId}/stared`)
        return result.data
    }, {
        enabled: isAuthed(),
    })
    const handleClick = async () => {
        toggleStared.mutate(data.stared)
    }
    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick()
    })

    return <Button
        ref={ref}
        isLoading={isInitialLoading || toggleStared.isLoading}
        colorScheme={'green'}
        variant={data?.stared ? 'solid' : 'outline'}
        onClick={handleClick}
        leftIcon={<StarIcon />}
        style={focused ? focusedBorder : null}
    >
        {data?.stared ? 'Stared' : 'Star'}
    </Button>
}