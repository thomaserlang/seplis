import { Stack } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { IMovie } from '@seplis/interfaces/movie'
import { ISeries, ISeriesAndEpisode } from '@seplis/interfaces/series'
import { IUserWatched } from '@seplis/interfaces/user_watched'
import { episodeNumber, setTitle } from '@seplis/utils'
import { useCallback, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'


export default function WatchHome() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        setTitle('Watch Home')
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

    const itemSelected = useCallback((item: ISeriesAndEpisode) => {
        navigate(`/series/${item.series.id}`, { state: { background: location } })
    }, [])

    const seriesSelected = useCallback((series: ISeries) => {
        navigate(`/series/${series.id}`, { state: { background: location } })
    }, [])

    const movieSelected = useCallback((movie: IMovie) => {
        navigate(`/movies/${movie.id}`, { state: { background: location } })
    }, [])

    const userWatchedSelected = useCallback((item: IUserWatched) => {
        if (item.type == 'series')
            seriesSelected(item.data as ISeries)
        else if (item.type == 'movie')
            movieSelected(item.data as IMovie)
    }, [])

    return <>
        <MainMenu />

        <FocusContext.Provider value={focusKey}>

            <Stack ref={ref} marginTop="0.5rem" marginBottom="0.5rem">

                <Slider<IUserWatched>
                    title="Watched"
                    url="/2/users/me/watched?user_can_watch=true"
                    parseItem={(item) => (
                        {
                            key: `${item.type}-${item.data.id}`,
                            title: item.data.title,
                            img: item.data.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={userWatchedSelected}
                    hideIfEmpty={true}
                />

                <Slider<ISeriesAndEpisode>
                    title="Series to Watch"
                    url="/2/users/me/series-to-watch?user_can_watch=true"
                    parseItem={(item) => (
                        {
                            key: `series-${item.series.id}`,
                            title: item.series.title,
                            img: item.series.poster_image?.url,
                            bottomText: episodeNumber(item.episode),
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                    hideIfEmpty={true}
                />

                <Slider<ISeriesAndEpisode>
                    title="Episodes recently aired"
                    url="/2/series-recently-aired?user_can_watch=true"
                    parseItem={(item) => (
                        {
                            key: `series-${item.series.id}`,
                            title: item.series.title,
                            img: item.series.poster_image?.url,
                            bottomText: episodeNumber(item.episode),
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                    hideIfEmpty={true}
                />


                <Slider<IMovie>
                    title="Movies recently added"
                    url="/2/movies?user_can_watch=true&sort=user_play_server_movie_added_desc"
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={movieSelected}
                    hideIfEmpty={true}
                />

                <Slider<ISeries>
                    title="Series recently added"
                    url="/2/series?user_can_watch=true&sort=user_play_server_series_added_desc"
                    parseItem={(series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={seriesSelected}
                    hideIfEmpty={true}
                />
                
                <Slider<ISeries>
                    title="Popular series"
                    url="/2/series?user_can_watch=true&sort=popularity_desc"
                    parseItem={(series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={seriesSelected}
                    hideIfEmpty={true}
                />

                <Slider<IMovie>
                    title="Popular movies"
                    url="/2/movies?user_can_watch=true&sort=popularity_desc"
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={movieSelected}
                    hideIfEmpty={true}
                />

                <Slider<ISeries>
                    title="Series following"
                    url="/2/series?user_following=true&user_can_watch=true&sort=user_followed_at_desc"
                    parseItem={(series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={seriesSelected}
                    hideIfEmpty={true}
                />

                <Slider<IMovie>
                    title="Movies stared"
                    url="/2/movies?user_stared=true&user_can_watch=true&sort=user_stared_at_desc"
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={movieSelected}
                    hideIfEmpty={true}
                />


                <Slider<ISeries>
                    title="Series you haven't watched"
                    url="/2/series?user_has_watched=false&user_can_watch=true"
                    parseItem={(series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={seriesSelected}
                    hideIfEmpty={true}
                />

                <Slider<IMovie>
                    title="Movies you haven't watched"
                    url="/2/movies?user_has_watched=false&user_can_watch=true"
                    parseItem={(movie) => (
                        {
                            key: `movie-${movie.id}`,
                            title: movie.title,
                            img: movie.poster_image?.url,
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={movieSelected}
                    hideIfEmpty={true}
                />

            </Stack>
        </FocusContext.Provider>
    </>
}