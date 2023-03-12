import { useToast } from '@chakra-ui/react'
import api from '@seplis/api'
import { EVENT_MOVIE_WATCHED, TriggerMovieWatched, useEventListener } from '@seplis/events'
import { useEffect, useState } from 'react'
import { ErrorMessageFromResponse } from '../error'
import { IEventMovieWatched, IMovieWatched, IMovieWatchedDefault } from '@seplis/interfaces/movie'
import { WatchedButton } from '../watched-button'
import { useQuery } from '@tanstack/react-query'
import { isAuthed } from '@seplis/utils'


export function MovieWatchedButtonData({ movieId, data }: { movieId: number, data: IMovieWatched }) {
    if (!data) data = IMovieWatchedDefault(0)
    const toast = useToast()
    const [watched, setWatched] = useState<IMovieWatched>(data)
    const [isUpdating, setUpdating] = useState(false)
    
    useEventListener<IEventMovieWatched>(EVENT_MOVIE_WATCHED, ((data) => {
        if (data.movieId == movieId)
            setWatched({ ...data.watched })
    }), [movieId])

    useEffect(() => {
        if (data != watched)
            setWatched({ ...data })
    }, [data])

    const increment = async () => {
        try {
            setUpdating(true)
            const r = await api.post<IMovieWatched>(`/2/movies/${movieId}/watched`)
            TriggerMovieWatched(movieId, r.data)
        } catch (e) {
            toast({
                title: ErrorMessageFromResponse(e),
                status: 'error',
                isClosable: true,
                position: 'top',
            })
        } finally {
            setUpdating(false)
        }
    }

    const decrement = async () => {
        try {
            setUpdating(true)
            const r = await api.delete<IMovieWatched>(`/2/movies/${movieId}/watched`)
            TriggerMovieWatched(movieId, r.data)
        } catch (e) {
            toast({
                title: ErrorMessageFromResponse(e),
                status: 'error',
                isClosable: true,
                position: 'top',
            })
        } finally {
            setUpdating(false)
        }
    }

    return <WatchedButton
        times={watched.times}
        position={watched.position}
        onIncrement={increment}
        onDecrement={decrement}
        isUpdating={isUpdating}
    />
}

export function MovieWatchedButton({ movieId }: { movieId: number }) {
    const { isInitialLoading, data } = useQuery(['movie', movieId, 'watched'], async () => {
        const result = await api.get<IMovieWatched>(`/2/movies/${movieId}/watched`)
        return result.data
    }, {
        enabled: isAuthed(),
    })
    return <>{isInitialLoading ?
        <WatchedButton
            isUpdating={true}
        /> : <MovieWatchedButtonData
            movieId={movieId}
            data={data}
        />}
    </>
}