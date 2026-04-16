import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import {
    PlayServerCreate,
    PlayServerUpdate,
    PlayServerWithUrl,
} from '../types/play-server.types'

interface PlayServerGetProps extends ApiHelperProps<{}> {
    playServerId: string
}

export const {
    get: getPlayServer,
    useGet: useGetPlayServer,
    queryKey: playServerQueryKey,
} = useApiHelper<PlayServerWithUrl, PlayServerGetProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}`,
    queryKey: ({ playServerId }) => ['play-server', playServerId],
})

interface PlayServerCreateProps extends MutationApiHelperProps<PlayServerCreate> {}

export const {
    mutation: createPlayServer,
    useMutation: useCreatePlayServer,
} = useMutationApiHelper<PlayServerWithUrl, PlayServerCreateProps>({
    url: () => '/2/play-servers',
    method: 'POST',
})

interface PlayServerUpdateProps extends MutationApiHelperProps<PlayServerUpdate> {
    playServerId: string
}

export const {
    mutation: updatePlayServer,
    useMutation: useUpdatePlayServer,
} = useMutationApiHelper<PlayServerWithUrl, PlayServerUpdateProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}`,
    method: 'PUT',
})

interface PlayServerDeleteProps extends MutationApiHelperProps<{}> {
    playServerId: string
}

export const {
    mutation: deletePlayServer,
    useMutation: useDeletePlayServer,
} = useMutationApiHelper<void, PlayServerDeleteProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}`,
    method: 'DELETE',
})
