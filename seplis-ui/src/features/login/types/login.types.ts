import { User } from '@/features/user/types/user.types'

export interface TokenCreate {
    login: string
    password: string
    client_id: string
    grant_type: 'password'
}

export interface Token {
    access_token: string
}

export interface UserLoggedIn extends User {
    token: string
}

export type UsersLoggedIn = { [key: string]: UserLoggedIn }
