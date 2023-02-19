import { Button, Icon } from '@chakra-ui/react'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import api from '@seplis/api'
import { IPlayRequest } from '@seplis/interfaces/play-server'
import { focusedBorder } from '@seplis/styles'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { FaPlay } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'


export default function PlayButton({ movieId }: { movieId: number }) {
    const navigate = useNavigate()
    const { isInitialLoading, data } = useQuery(['movie', 'play-button', movieId], async () => {
        const result = await api.get<IPlayRequest[]>(`/2/movies/${movieId}/play-servers`)
        return result.data.length > 0
    }, {
        enabled: isAuthed()
    })
    const handleClick = () => {
        navigate(`/movies/${movieId}/play`)
    }
    const { ref, focused } = useFocusable({
        focusKey: 'MOVIE_PLAY',
        focusable: data,
        onEnterPress: () => {
            handleClick()
        }
    })
    return <Button
        ref={ref}
        isLoading={isInitialLoading}
        leftIcon={<Icon as={FaPlay} />}
        style={focused ? focusedBorder : null}
        disabled={!data}
        onClick={handleClick}
    >
        Play
    </Button>
}