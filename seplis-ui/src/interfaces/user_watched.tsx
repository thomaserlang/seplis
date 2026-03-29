import { IMovie } from "./movie"
import { ISeries } from "./series"


export interface IUserWatched {
    type: string
    data: IMovie | ISeries
}