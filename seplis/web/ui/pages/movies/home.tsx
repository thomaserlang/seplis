import { Stack } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { IMovieUser } from '@seplis/interfaces/movie'
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

    const itemSelected = (item: IMovieUser) => {
        navigate(`/movies/${item.movie.id}`, {state: {
            background: location
        }})
    }

    return <>
        <MainMenu />
        
        <FocusContext.Provider value={focusKey}>
            <Stack ref={ref} marginTop="0.5rem">
                <Slider<IMovieUser>
                    title="Watched"
                    url="/2/users/me/movies-watched"
                    parseItem={(item) => (
                        {
                            key: `movie-${item.movie.id}`,
                            title: item.movie.title,
                            img: item.movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />

                <Slider<IMovieUser>
                    title="Stared"
                    url="/2/users/me/movies-stared"
                    parseItem={(item) => (
                        {
                            key: `movie-${item.movie.id}`,
                            title: item.movie.title,
                            img: item.movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                />
            </Stack>
        </FocusContext.Provider>
    </>
}