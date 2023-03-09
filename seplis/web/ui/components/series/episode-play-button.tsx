import { Box, Button } from '@chakra-ui/react'
import { FaPlay } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import Chromecast from '../player/Chromecast'


export function PlayButton({ seriesId, episodeNumber, canPlay }: { seriesId: number, episodeNumber: number, canPlay: boolean }) {
    const navigate = useNavigate()
    const cast = new Chromecast()
    if (!canPlay)
        return null
    return <Box>
        <Button
            leftIcon={<FaPlay />}
            onClick={() => {
                if (cast.isConnected())
                    cast.playEpisode(seriesId, episodeNumber)
                else
                    navigate(`/series/${seriesId}/episodes/${episodeNumber}/play`)
            }}
        >
            Play
        </Button>
    </Box>
}