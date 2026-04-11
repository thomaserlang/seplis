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
        queryClient.setQueryData(
            getEpisodeWatchedQueryKey({
                seriesId: variables.seriesId,
                episodeNumber: variables.episodeNumber,
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
        queryClient.setQueryData(
            getEpisodeWatchedQueryKey({
                seriesId: variables.seriesId,
                episodeNumber: variables.episodeNumber,
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
