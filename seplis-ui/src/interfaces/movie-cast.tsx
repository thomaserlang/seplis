import { IPerson } from './person'

export interface IMovieCastPerson {
    person: IPerson
    character: string | null
    order: number | null
}