import api from '@seplis/api'
import Player from '@seplis/components/player/player'
import { IMovie, IMovieWatched } from '@seplis/interfaces/movie'
import { useQuery } from '@tanstack/react-query'
import { useRef } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'


export default function PlayMovie() {
    const { movieId } = useParams()
    const navigate = useNavigate()
    const location = useLocation()

    const movie = useQuery(['movie-title-watched', movieId], async () => {
        const result = await Promise.all([
            api.get<IMovie>(`/2/movies/${movieId}`),
            api.get<IMovieWatched>(`/2/movies/${movieId}/watched`),
        ])
        return {
            title: `${result[0].data.title}`,
            startTime: result[1].data?.position ?? 0,
        }
    })

    const markedAsWatched = useRef(false)
    const prevSavedPosition = useRef(0)
    const onTimeUpdate = (time: number, duration: number) => {
        if ((time === movie.data.startTime) || (time === prevSavedPosition.current) || (time < 10) || ((time % 10) != 0))
            return
        const watched = (((time / 100) * 10) > (duration - time))
        prevSavedPosition.current = time
        if (watched) {
            if (!markedAsWatched.current) {
                markedAsWatched.current = true
                api.post(`/2/movies/${movieId}/watched`).catch(() => {
                    markedAsWatched.current = false
                })
            }
        } else {
            markedAsWatched.current = false
            api.put(`/2/movies/${movieId}/watched-position`, {
                position: time
            })
        }
    }

    return <Player
        getPlayServersUrl={`/2/movies/${movieId}/play-servers`}
        title={movie.data?.title}
        startTime={movie.data?.startTime}
        onTimeUpdate={onTimeUpdate}
        loading={movie.isLoading}
        onClose={() => {
            if (location.key && location.key != 'default')
                navigate(-1)
            else
                navigate(`/movies/${movieId}`)
        }}
    />
}