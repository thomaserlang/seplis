import { Box } from '@mantine/core'
import { useNavigate, useParams } from 'react-router-dom'
import { useGetSeries } from '../series/api/series.api'
import { useGetEpisode } from './api/episode.api'
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

    const { data: series } = useGetSeries({ seriesId: sid })
    const { data: episode } = useGetEpisode({ seriesId: sid, number: epNum })

    const title = series?.title
    const subtitle = episode
        ? `S${episode.season} E${episode.episode}${episode.title ? ` - ${episode.title}` : ''}`
        : undefined

    return (
        <Box h="100dvh" w="100dvw">
            <EpisodePlayView
                seriesId={sid}
                episodeNumber={epNum}
                title={title}
                subtitle={subtitle}
                onClose={() => navigate(-1)}
            />
        </Box>
    )
}
