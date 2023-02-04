import { Button, Icon } from "@chakra-ui/react"
import { useFocusable } from "@noriginmedia/norigin-spatial-navigation"
import api from "@seplis/api"
import { IPlayRequest } from "@seplis/interfaces/play-server-request"
import { focusedBorder } from "@seplis/styles"
import { isAuthed } from "@seplis/utils"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { FaPlay } from "react-icons/fa"
import { useNavigate } from "react-router-dom"


export default function PlayButton({ movieId }: { movieId: number }) {
    const [canPlay, setCanPlay] = useState(false)
    const navigate = useNavigate()
    const { isInitialLoading } = useQuery(['play-button', 'movie', movieId], async () => {
        if (!isAuthed())
            return
        const result = await api.get<IPlayRequest[]>(`/2/movies/${movieId}/play-servers`)
        setCanPlay(result.data.length > 0)
        return result.data
    })
    const handleClick = () => {
        navigate(`/movies/${movieId}/play`)
    }
    const { ref, focused } = useFocusable({
        focusKey: 'MOVIE_PLAY',
        focusable: canPlay,
        onEnterPress: () => {
            handleClick()
        }
    })
    return <Button
        ref={ref}
        isLoading={isInitialLoading}
        leftIcon={<Icon as={FaPlay} />}
        style={focused ? focusedBorder : null}
        disabled={!canPlay}
        onClick={handleClick}
    >
        Play
    </Button>
}