import { IImage } from "./image"
import { TExternals } from "./types"


export interface IPerson {
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
    externals: TExternals
}