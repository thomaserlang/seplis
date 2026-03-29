import { DependencyList, useEffect } from 'react'
import { IEpisodeWatched, IEventEpisodeWatched } from './interfaces/episode'
import { IEventMovieWatched, IMovieWatched } from './interfaces/movie'

export const EVENT_EPISODE_WATCHED = 'EpisodeWatched'
export function TriggerEpisodeWatched(seriesId: number, episodeNumber: number, watched: IEpisodeWatched) {
    const e = new CustomEvent<IEventEpisodeWatched>(EVENT_EPISODE_WATCHED, {
        detail: {
            seriesId: seriesId,
            episodeNumber: episodeNumber,
            watched: watched,
        }
    })
    window.dispatchEvent(e)
}


export const EVENT_MOVIE_WATCHED = 'MovieWatched'
export function TriggerMovieWatched(movieId: number, watched: IMovieWatched) {
    const e = new CustomEvent<IEventMovieWatched>(EVENT_MOVIE_WATCHED, {
        detail: {
            movieId: movieId,
            watched: watched,
        }
    })
    window.dispatchEvent(e)
}



export function useEventListener<T = any>(eventName: string, handler: (data: T) => void, deps?: DependencyList) {
    useEffect(() => {
        const handleEvent = (event: CustomEvent<T>) => {
            handler(event.detail)
        }
        window.addEventListener(eventName, (handleEvent as EventListener))
        return () => {
            window.removeEventListener(eventName, (handleEvent as EventListener))
        }
    }, deps)
}