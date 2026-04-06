import { Box } from '@mantine/core'
import { useParams } from 'react-router-dom'
import { EpisodePlayView } from './components/episode-play-view'

export function Component() {
    const { seriesId, episodeNumber } = useParams<{
        seriesId?: string
        episodeNumber?: string
    }>()

    if (!seriesId) throw new Error('Missing seriesId')
    if (!episodeNumber) throw new Error('Missing episodeNumber')

    return (
        <Box h="100dvh" w="100dvw">
            <EpisodePlayView
                seriesId={Number(seriesId)}
                episodeNumber={Number(episodeNumber)}
            />
        </Box>
    )
}
