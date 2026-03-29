import { IPerson } from './person'


export interface ISeriesCastRole {
    character: string | null
    total_episodes: number | null
}


export interface ISeriesCastPerson {
    person: IPerson
    roles: ISeriesCastRole[]
    order: number | null
    total_episodes: number
}
