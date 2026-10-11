import { getPlayRequestSources } from '@/features/play'
import { ApiHelperProps, fetchAllPages, useApiHelper } from '@/utils/api-crud'
import { Episode } from '../types/episode.types'
import { getEpisodePlayRequests } from './episode-play-requests.api'
import { getEpisodes } from './episodes.api'

interface RandomEpisodeGetProps extends ApiHelperProps {
    seriesId: number
}

export const {
    get: getRandomPlayableEpisode,
    useGet: useGetRandomPlayableEpisode,
} = useApiHelper<Episode | null, RandomEpisodeGetProps>({
    url: () => '',
    queryKey: ({ seriesId }) => ['series', seriesId, 'random-episode'],
    getFn: async ({ seriesId, signal }) => {
        const now = new Date()
        const today = now.toISOString().slice(0, 10)
        const episodes = await fetchAllPages(getEpisodes, {
            seriesId,
            signal,
            params: { air_date_le: today, per_page: 100 },
        })
        const candidates = episodes.filter((episode) =>
            episode.air_datetime
                ? new Date(episode.air_datetime).getTime() <= now.getTime()
                : !!episode.air_date && episode.air_date <= today,
        )

        while (candidates.length) {
            signal?.throwIfAborted()
            const index = Math.floor(Math.random() * candidates.length)
            const [episode] = candidates.splice(index, 1)
            const playRequests = await getEpisodePlayRequests({
                seriesId,
                episodeNumber: episode.number,
                signal,
            })
            if (!playRequests.length) continue

            const sources = await getPlayRequestSources({
                playRequests,
                signal,
            })
            signal?.throwIfAborted()
            if (sources.some((source) => source.sources.length > 0))
                return episode
        }

        return null
    },
})
