import { Box } from '@mantine/core'
import { useNavigate, useParams } from 'react-router-dom'
import { EpisodePlayView } from './components/episode-play-view'

export function Component() {
    const { seriesId, episodeNumber } = useParams<{
        seriesId?: string
        episodeNumber?: string
    }>()
    const navigate = useNavigate()

    if (!seriesId) throw new Error('Missing seriesId')
    if (!episodeNumber) throw new Error('Missing episodeNumber')

    const sid = Number(seriesId)
    const epNum = Number(episodeNumber)

    return (
        <Box h="100dvh" w="100dvw">
            <EpisodePlayView
                key={`${sid}-${epNum}`}
                seriesId={sid}
                episodeNumber={epNum}
                onClose={() => navigate(-1)}
            />
        </Box>
    )
}
