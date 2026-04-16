export interface PlayServerCreate {
    name: string
    url: string
    secret: string
}

export interface PlayServerUpdate {
    name?: string | null
    url?: string | null
    secret?: string | null
}

export interface PlayServer {
    id: string
    name: string
}

export interface PlayServerWithUrl extends PlayServer {
    url: string
}

export interface PlayServerWithSecret extends PlayServerWithUrl {
    secret: string
}
