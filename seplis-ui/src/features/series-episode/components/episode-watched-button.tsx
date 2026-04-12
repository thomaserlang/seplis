import { WatchedButton } from '@/components/watched-button'
import { useActiveUser } from '@/features/user'
import { queryClient } from '@/queryclient'
import { toastError } from '@/utils/toast'
import { ButtonSize } from '@mantine/core'
import { useEffect } from 'react'
import {
    getEpisodeWatchedQueryKey,
    useDecrementEpisodeWatched,
    useGetEpisodeWatched,
    useIncrementEpisodeWatched,
} from '../api/episode-watched.api'
import { Episode } from '../types/episode.types'

interface Props {
    seriesId: number
    episodeNumber: number
    episode?: Episode
    size?: ButtonSize
}

export function EpisodeWatchedButton({
    seriesId,
    episodeNumber,
    episode,
    size,
}: Props) {
    const [user] = useActiveUser()

    useEffect(() => {
        if (episode?.user_watched !== undefined) {
            queryClient.setQueryData(
                getEpisodeWatchedQueryKey({ seriesId, episodeNumber }),
                episode.user_watched,
            )
        }
    }, [episode?.user_watched, seriesId, episodeNumber])

    const { data, isLoading } = useGetEpisodeWatched({
        seriesId,
        episodeNumber,
        options: {
            enabled: !!user && episode?.user_watched === undefined,
            initialData: episode?.user_watched ?? undefined,
        },
    })
    const increment = useIncrementEpisodeWatched({
        onError: (e) => {
            toastError(e)
        },
    })
    const decrement = useDecrementEpisodeWatched({
        onError: (e) => {
            toastError(e)
        },
    })

    return (
        <WatchedButton
            times={data?.times ?? 0}
            position={data?.position ?? 0}
            duration={episode?.runtime ?? 0}
            loading={isLoading}
            size={size}
            onIncrement={() =>
                increment.mutate({ seriesId, episodeNumber: episodeNumber })
            }
            onDecrement={() =>
                decrement.mutate({ seriesId, episodeNumber: episodeNumber })
            }
        />
    )
}
