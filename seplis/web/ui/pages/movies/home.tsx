import { Stack } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { IMovie } from '@seplis/interfaces/movie'
import { setTitle } from '@seplis/utils'
import { useCallback, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'


export default function MoviesHome() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()
    
    useEffect(() => {
        setTitle('Movies Home')
    }, [])

    useEffect(() => {
        focusSelf()
    }, [focusSelf])

    const onRowFocus = useCallback(({ y }: { y: number }) => {
        window.scrollTo({
            top: y,
            behavior: 'smooth'
        });
    }, [ref])

    const itemSelected = (movie: IMovie) => {
        navigate(`/movies/${movie.id}`, {state: {
            background: location
        }})
    }

    return <>
        <MainMenu active="movies" />
        
        <FocusContext.Provider value={focusKey}>
            <Stack ref={ref} marginTop="0.5rem">
                <Slider<IMovie>
                    title="Watched"
                    url="/2/movies?user_has_watched=true&sort=user_last_watched_at_desc"
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />

                <Slider<IMovie>
                    title="Watchlist"
                    url="/2/movies?user_watchlist=true&sort=user_watchlist_added_at_desc"
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />
            </Stack>
        </FocusContext.Provider>
    </>
}