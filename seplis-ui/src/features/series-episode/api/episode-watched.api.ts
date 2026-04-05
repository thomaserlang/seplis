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
    queryKey: episodeWatchedQueryKey,
} = useApiHelper<EpisodeWatched, EpisodeWatchedGetProps>({
    url: ({ seriesId, episodeNumber: episodeId }) =>
        `2/series/${seriesId}/episodes/${episodeId}/watched`,
    queryKey: ({ seriesId, episodeNumber: episodeId }) => [
        'episode-watched',
        seriesId,
        episodeId,
    ],
})

interface EpisodeWatchedIncrementProps extends MutationApiHelperProps<{}> {
    seriesId: number
    episodeId: number
}

export const {
    mutation: episodeIncrementWatched,
    useMutation: useIncrementEpisodeWatched,
} = useMutationApiHelper<EpisodeWatched, EpisodeWatchedIncrementProps>({
    method: 'POST',
    url: ({ seriesId, episodeId }) =>
        `2/series/${seriesId}/episodes/${episodeId}/watched`,
    onSuccess: ({ data, variables }) => {
        queryClient.setQueryData(
            episodeWatchedQueryKey({
                seriesId: variables.seriesId,
                episodeNumber: variables.episodeId,
            }),
            data,
        )
        queryClient.invalidateQueries({
            queryKey: episodeLastWatchedQueryKey({
                seriesId: variables.seriesId,
            }),
        })
        queryClient.invalidateQueries({
            queryKey: episodeToWatchQueryKey({ seriesId: variables.seriesId }),
        })
    },
})

interface EpisodeWatchedDecrementProps extends MutationApiHelperProps<{}> {
    seriesId: number
    episodeId: number
}

export const {
    mutation: episodeDecrementWatched,
    useMutation: useDecrementEpisodeWatched,
} = useMutationApiHelper<EpisodeWatched, EpisodeWatchedDecrementProps>({
    method: 'DELETE',
    url: ({ seriesId, episodeId }) =>
        `2/series/${seriesId}/episodes/${episodeId}/watched`,
    onSuccess: ({ data, variables }) => {
        queryClient.setQueryData(
            episodeWatchedQueryKey({
                seriesId: variables.seriesId,
                episodeNumber: variables.episodeId,
            }),
            data,
        )
        queryClient.invalidateQueries({
            queryKey: episodeLastWatchedQueryKey({
                seriesId: variables.seriesId,
            }),
        })
        queryClient.invalidateQueries({
            queryKey: episodeToWatchQueryKey({ seriesId: variables.seriesId }),
        })
    },
})
