import { Box, Button } from '@chakra-ui/react'
import { FaPlay } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'


export function PlayButton({ seriesId, episodeNumber, canPlay }: { seriesId: number, episodeNumber: number, canPlay: boolean }) {
    const navigate = useNavigate()
    const click = () => {
        navigate(`/series/${seriesId}/episodes/${episodeNumber}/play`)
    }
    if (!canPlay)
        return null
    return <Box>
        <Button
            leftIcon={<FaPlay />}
            onClick={click}
        >
            Play
        </Button>
    </Box>
}