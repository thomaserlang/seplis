import {
    ApiHelperProps,
    MutationApiHelperProps,
    useMutationApiHelper,
    usePageApiHelper,
} from '@/utils/api-crud'
import { PlayServerWithUrl } from '../types/play-server.types'
import { PlayServerAccess } from '../types/play-server-invite.types'

interface PlayServerAccessGetProps extends ApiHelperProps<{}> {
    playServerId: string
}

interface AccessiblePlayServersGetProps extends ApiHelperProps<{}> {}

export const {
    getPage: getAccessiblePlayServers,
    useGetPage: useGetAccessiblePlayServers,
    queryKey: accessiblePlayServersQueryKey,
} = usePageApiHelper<PlayServerWithUrl, AccessiblePlayServersGetProps>({
    url: () => '/2/play-servers/access',
    queryKey: ({ params }) => ['play-servers', 'access', params].filter(Boolean),
})

export const {
    getPage: getPlayServerAccess,
    useGetPage: useGetPlayServerAccess,
    queryKey: playServerAccessQueryKey,
} = usePageApiHelper<PlayServerAccess, PlayServerAccessGetProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}/access`,
    queryKey: ({ playServerId, params }) =>
        ['play-server', playServerId, 'access', params].filter(Boolean),
})

interface RemovePlayServerAccessProps extends MutationApiHelperProps<{}> {
    playServerId: string
    userId: string
}

export const {
    mutation: removePlayServerAccess,
    useMutation: useRemovePlayServerAccess,
} = useMutationApiHelper<void, RemovePlayServerAccessProps>({
    url: ({ playServerId, userId }) =>
        `/2/play-servers/${playServerId}/acceess/${userId}`,
    method: 'DELETE',
})

interface LeavePlayServerProps extends MutationApiHelperProps<{}> {
    playServerId: string
}

export const {
    mutation: leavePlayServer,
    useMutation: useLeavePlayServer,
} = useMutationApiHelper<void, LeavePlayServerProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}/access/me`,
    method: 'DELETE',
})
