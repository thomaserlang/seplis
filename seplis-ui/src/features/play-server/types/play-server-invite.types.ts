import { UserPublic } from '@/features/user'

export interface PlayServerInviteCreate {
    user_id: number
}

export interface PlayServerInviteId {
    invite_id: string
}

export interface PlayServerInvite {
    user: UserPublic
    created_at: string
    expires_at: string
}

export interface PlayServerAccess {
    user: UserPublic
    created_at: string
}
