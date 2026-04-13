import { getUserWatchedQueryKey } from '@/features/user'
import { queryClient } from '@/queryclient'
import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import { EpisodeWatched } from '../types/episode.types'
import { episodeLastWatchedQueryKey } from './episode-last-watched.api'
import { episodeToWatchQueryKey } from './episode-to-watch.api'

interface EpisodeWatchedGetProps extends ApiHelperProps<{}> {
    seriesId: number
    episodeNumber: number
}

export const {
    get: getEpisodeWatched,
    useGet: useGetEpisodeWatched,
    queryKey: getEpisodeWatchedQueryKey,
} = useApiHelper<EpisodeWatched, EpisodeWatchedGetProps>({
    url: ({ seriesId, episodeNumber }) =>
        `2/series/${seriesId}/episodes/${episodeNumber}/watched`,
    queryKey: ({ seriesId, episodeNumber }) => [
        'episode-watched',
        seriesId,
        episodeNumber,
    ],
})

interface EpisodeWatchedIncrementProps extends MutationApiHelperProps<{}> {
    seriesId: number
    episodeNumber: number
}

export const {
    mutation: incrementEpisodeWatched,
    useMutation: useIncrementEpisodeWatched,
} = useMutationApiHelper<EpisodeWatched, EpisodeWatchedIncrementProps>({
    method: 'POST',
    url: ({ seriesId, episodeNumber }) =>
        `2/series/${seriesId}/episodes/${episodeNumber}/watched`,
    onSuccess: ({ data, variables }) => {
        invalidateEpisodeWatched({
            seriesId: variables.seriesId,
            episodeNumber: variables.episodeNumber,
            data,
        })
    },
})

interface EpisodeWatchedDecrementProps extends MutationApiHelperProps<{}> {
    seriesId: number
    episodeNumber: number
}

export const {
    mutation: decrementEpisodeWatched,
    useMutation: useDecrementEpisodeWatched,
} = useMutationApiHelper<EpisodeWatched, EpisodeWatchedDecrementProps>({
    method: 'DELETE',
    url: ({ seriesId, episodeNumber }) =>
        `2/series/${seriesId}/episodes/${episodeNumber}/watched`,
    onSuccess: ({ data, variables }) => {
        invalidateEpisodeWatched({
            seriesId: variables.seriesId,
            episodeNumber: variables.episodeNumber,
            data,
        })
    },
})

export function invalidateEpisodeWatched({
    seriesId,
    episodeNumber,
    data,
}: {
    seriesId: number
    episodeNumber: number
    data?: EpisodeWatched
}) {
    if (data) {
        queryClient.setQueryData(
            getEpisodeWatchedQueryKey({
                seriesId,
                episodeNumber,
            }),
            data,
        )
    } else {
        queryClient.invalidateQueries({
            queryKey: getEpisodeWatchedQueryKey({ seriesId, episodeNumber }),
        })
    }
    queryClient.invalidateQueries({
        queryKey: episodeLastWatchedQueryKey({ seriesId }),
    })
    queryClient.invalidateQueries({
        queryKey: episodeToWatchQueryKey({ seriesId }),
    })
    queryClient.invalidateQueries({
        queryKey: getUserWatchedQueryKey({}),
    })
}
