import { Box, Button, Link } from '@chakra-ui/react'
import { IEpisode } from '@seplis/interfaces/episode'
import { FaPlay } from 'react-icons/fa'
import { Link as ReactRouterLink, useNavigate } from 'react-router-dom'


export function PlayButton({ seriesId, episode }: { seriesId: number, episode: IEpisode }) {
    const navigate = useNavigate()
    const click = () => {
        navigate(`/series/${seriesId}/episodes/${episode.number}/play`)
    }
    if (!episode.user_can_watch || !episode.user_can_watch.on_play_server)
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