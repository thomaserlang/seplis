import { IImage } from './image.types'

export interface Person {
    id: number
    name: string
    also_known_as: string[]
    gender: number | null
    birthday: string | null
    deathday: string | null
    biography: string | null
    place_of_birth: string | null
    profile_image: IImage | null
    popularity: number | null
    externals: Record<string, string>
}

export interface CastMember {
    person: Person
    roles?: CastMemberRole[]
    character?: string
    total_episodes: number
}

export interface CastMemberRole {
    character: string
    total_episodes: number
}
