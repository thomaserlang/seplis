import { useActiveUser } from '@/features/user'
import { useGetEpisodeLastWatched } from '../api/episode-last-watched.api'
import { EpisodeCard } from './episode-card'

interface Props {
    seriesId: number
}

export function EpisodeLastWatchedCard({ seriesId }: Props) {
    const [user] = useActiveUser()
    const { data, isLoading } = useGetEpisodeLastWatched({
        seriesId,
        options: {
            enabled: !!user,
        },
    })

    if (!user) return

    return (
        <EpisodeCard
            seriesId={seriesId}
            episode={data}
            loading={isLoading}
            title="Last watched"
            accentColor="oklch(0.4 0.07 240)"
            noEpisodeText="No episode watched yet"
        />
    )
}
