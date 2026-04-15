import { MediaTypeInfo } from '@/features/media-type/types/media-type-registry.types'
import { EpisodePlayView } from '../components/episode-play-view'
import { Episode } from '../types/episode.types'

export const episodeMediaInfo: MediaTypeInfo<Episode> = {
    name: 'Episode',
    color: 'blue',
    mediaType: 'episode',
    accentHue: 250,
    render: () => <></>,
    renderHoverCard: () => <></>,
    player: ({ itemId, onClose }) => {
        const [sid, epNum] = itemId.split(':')
        return (
            <EpisodePlayView
                key={itemId}
                seriesId={Number(sid)}
                episodeNumber={Number(epNum)}
                onClose={onClose}
            />
        )
    },
}
