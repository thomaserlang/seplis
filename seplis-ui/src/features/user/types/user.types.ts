export interface User {
    id: number
    username: string
    created_at: string
    scopes: string
}

export interface UserPublic {
    id: number
    username: string
}

export interface UserCreate {
    username: string
    password: string
    email: string
}
