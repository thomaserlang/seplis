export interface IUser {
    id: number
    username: string
    created_at: string
    level: number
}

export interface IUserLoggedIn extends IUser {
    token: string
}

export type IUsersLoggedIn = { [key: string]: IUserLoggedIn }