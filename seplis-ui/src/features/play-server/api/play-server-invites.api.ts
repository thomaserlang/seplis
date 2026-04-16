import {
    ApiHelperProps,
    MutationApiHelperProps,
    useMutationApiHelper,
    usePageApiHelper,
} from '@/utils/api-crud'
import {
    PlayServerInvite,
    PlayServerInviteCreate,
    PlayServerInviteId,
} from '../types/play-server-invite.types'

interface PlayServerInvitesGetProps extends ApiHelperProps<{}> {
    playServerId: string
}

export const {
    getPage: getPlayServerInvites,
    useGetPage: useGetPlayServerInvites,
    queryKey: playServerInvitesQueryKey,
} = usePageApiHelper<PlayServerInvite, PlayServerInvitesGetProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}/invites`,
    queryKey: ({ playServerId, params }) =>
        ['play-server', playServerId, 'invites', params].filter(Boolean),
})

interface PlayServerInviteCreateProps
    extends MutationApiHelperProps<PlayServerInviteCreate> {
    playServerId: string
}

export const {
    mutation: createPlayServerInvite,
    useMutation: useCreatePlayServerInvite,
} = useMutationApiHelper<PlayServerInviteId, PlayServerInviteCreateProps>({
    url: ({ playServerId }) => `/2/play-servers/${playServerId}/invites`,
    method: 'POST',
})

interface PlayServerInviteDeleteProps extends MutationApiHelperProps<void> {
    playServerId: string
    userId: string
}

export const {
    mutation: deletePlayServerInvite,
    useMutation: useDeletePlayServerInvite,
} = useMutationApiHelper<void, PlayServerInviteDeleteProps>({
    url: ({ playServerId, userId }) =>
        `/2/play-servers/${playServerId}/invites/${userId}`,
    method: 'DELETE',
})

interface PlayServerInviteAcceptProps
    extends MutationApiHelperProps<PlayServerInviteId> {}

export const {
    mutation: acceptPlayServerInvite,
    useMutation: useAcceptPlayServerInvite,
} = useMutationApiHelper<void, PlayServerInviteAcceptProps>({
    url: () => '/2/play-servers/accept-invite',
    method: 'POST',
})
