import { StarIcon } from '@chakra-ui/icons'
import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { isAuthed } from '@seplis/utils'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'
import { ISeriesFollowing } from '@seplis/interfaces/series'

const a = async (seriesId: number) => {
    await api.delete(`/2/series/${seriesId}/following`)
}

export default function FollowingButton({ seriesId }: { seriesId: number }) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleFollowing = useMutation(async (following: boolean) => {
        await queryClient.cancelQueries(['series', 'following-button', seriesId])
        let data: ISeriesFollowing
        if (following) {
            data = await api.delete(`/2/series/${seriesId}/following`)
        } else {
            data = await api.put(`/2/series/${seriesId}/following`)            
        }
        queryClient.setQueryData(['series', 'following-button', seriesId], { following: !following})
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

    const { isInitialLoading, data } = useQuery(['series', 'following-button', seriesId], async () => {
        const result = await api.get<ISeriesFollowing>(`/2/series/${seriesId}/following`)
        return result.data
    }, {
        enabled: isAuthed()
    })

    const handleClick = () => {
        toggleFollowing.mutate(data.following)
    }

    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick,
    })

    return <Button
        ref={ref}
        isLoading={isInitialLoading || toggleFollowing.isLoading}
        colorScheme={'green'}
        variant={data?.following ? 'solid' : 'outline'}
        onClick={handleClick}
        leftIcon={<StarIcon />}
        style={focused ? focusedBorder : null}
    >
        {data?.following ? 'Following' : 'Follow'}
    </Button>
}