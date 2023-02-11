import { StarIcon } from '@chakra-ui/icons'
import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'
import { ISeriesFollowing } from '@seplis/interfaces/series'

export default function StaredButton({ seriesId }: { seriesId: number }) {
    const toast = useToast()
    const [loading, setLoading] = useState(false)
    const [following, setFollowing] = useState(false)

    const { isInitialLoading } = useQuery(['series', 'following-button', seriesId], async () => {
        if (!isAuthed())
            return null
        const result = await api.get<ISeriesFollowing>(`/2/series/${seriesId}/following`)
        setFollowing(result.data.following)
        return result.data
    })
    const handleClick = async () => {
        setLoading(true)
        try {
            if (following) {
                await api.delete(`/2/series/${seriesId}/following`)
                setFollowing(false)
            } else {
                await api.put(`/2/series/${seriesId}/following`)
                setFollowing(true)
            }
        } catch (e) {
            toast({
                title: ErrorMessageFromResponse(e),
                status: 'error',
                isClosable: true,
                position: 'top',
            })

        } finally {
            setLoading(false)
        }
    }
    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick()
    })


    return <Button
        ref={ref}
        isLoading={isInitialLoading || loading}
        colorScheme={'green'}
        variant={following ? 'solid' : 'outline'}
        onClick={handleClick}
        leftIcon={<StarIcon />}
        style={focused ? focusedBorder : null}
    >
        {following ? 'Following' : 'Follow'}
    </Button>
}