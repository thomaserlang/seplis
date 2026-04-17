import { Box } from '@mantine/core'
import { useParams, useSearchParams } from 'react-router-dom'
import { EpisodePlayView } from './components/episode-play-view'

export function Component() {
    const { seriesId, episodeNumber } = useParams<{
        seriesId?: string
        episodeNumber?: string
    }>()
    const [_, setParams] = useSearchParams()

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
                onClose={() =>
                    setParams((params) => {
                        params.delete('pid')
                        return params
                    })
                }
            />
        </Box>
    )
}
