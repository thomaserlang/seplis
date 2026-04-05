import { useActiveUser } from '@/features/user'
import { useGetEpisodeToWatch } from '../api/episode-to-watch.api'
import { EpisodeCard } from './episode-card'

interface Props {
    seriesId: number
}

export function EpisodeToWatchCard({ seriesId }: Props) {
    const [user] = useActiveUser()
    const { data, isLoading } = useGetEpisodeToWatch({
        seriesId,
        options: {
            enabled: !!user,
        },
    })

    return (
        <EpisodeCard
            seriesId={seriesId}
            episode={data}
            loading={isLoading}
            title="Next to watch"
            accentColor="oklch(0.55 0.22 250)"
            noEpisodeText="No episode to watch"
        />
    )
}
