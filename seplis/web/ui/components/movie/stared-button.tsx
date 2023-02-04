import { StarIcon } from '@chakra-ui/icons'
import { Button, useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovieStared } from '@seplis/interfaces/movie'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { ErrorMessageFromResponse } from '../error'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { focusedBorder } from '@seplis/styles'

interface IProps {
    movieId: number
}

export default function StaredButton({ movieId }: IProps) {
    const toast = useToast()
    const [loading, setLoading] = useState(false)
    const [stared, setStared] = useState(false)

    const { isInitialLoading } = useQuery(['movie', movieId], async () => {
        if (!isAuthed())
            return        
        const result = await api.get<IMovieStared>(`/2/movies/${movieId}/stared`)
        setStared(result.data.stared)
        return result.data
    })
    const handleClick = async () => {
        setLoading(true)
        try {
            if (stared) {
                await api.delete(`/2/movies/${movieId}/stared`)
                setStared(false)
            } else {
                await api.put(`/2/movies/${movieId}/stared`)
                setStared(true)
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
        variant={stared?'solid':'outline'}
        onClick={handleClick}
        leftIcon={<StarIcon />}
        style={focused?focusedBorder:null}
    >
        {stared?'Stared':'Star'}
    </Button>
}