import { IEpisodeWatched, IEventEpisodeWatched } from "@seplis/interfaces/episode";
import { DependencyList, useEffect } from "react";

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