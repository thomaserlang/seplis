import { Alert, AlertIcon, Stack, Text } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { ISeries, ISeriesAndEpisode } from '@seplis/interfaces/series'
import { dateCountdown, episodeNumber, setTitle } from '@seplis/utils'
import { useCallback, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'


export default function SeriesHome() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        setTitle('Series Home')
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

    const itemSelected = (item: ISeriesAndEpisode) => {
        navigate(`/series/${item.series.id}`, {state: {
            background: location
        }})
    }
    const seriesSelected = (series: ISeries) => {
        navigate(`/series/${series.id}`, {state: {
            background: location
        }})
    }

    return <>
        <MainMenu active="series" />
        
        <FocusContext.Provider value={focusKey}>

            <Stack ref={ref} marginTop="0.5rem" marginBottom="0.5rem">

                <Slider<ISeries>
                    title="Watched"
                    url="/2/series?user_has_watched=true&sort=user_last_episode_watched_at_desc"
                    parseItem={(series) => (
                        {
                            key: `series-${series.id}`,
                            title: series.title,
                            img: series.poster_image?.url,
                            bottomText: episodeNumber(series.user_last_episode_watched),
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={seriesSelected}
                    emptyMessage={<Alert status='info'>
                        <AlertIcon />        
                        <Text>
                            You haven't watched anything.
                        </Text>
                    </Alert>}
                />

                <Slider<ISeriesAndEpisode>
                    title="Recently Aired"
                    url="/2/series-recently-aired?user_watchlist=true"
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
                    emptyMessage={<Alert status='info'>
                        <AlertIcon />        
                        <Text>
                            No series you follow has aired recently.
                        </Text>
                    </Alert>}
                />


                <Slider<ISeriesAndEpisode>
                    title="Countdown"
                    url="/2/users/me/series-countdown"
                    parseItem={(item) => (
                        {
                            key: `series-${item.series.id}`,
                            title: item.series.title,
                            img: item.series.poster_image?.url,
                            bottomText: episodeNumber(item.episode),
                            topText: dateCountdown(item.episode.air_datetime),
                        }
                    )}
                    onFocus={onRowFocus}
                    onItemSelected={itemSelected}
                    hideIfEmpty={true}
                />

                <Slider<ISeriesAndEpisode>
                    title="Series to Watch"
                    url="/2/users/me/series-to-watch"
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
                    emptyMessage={<Alert status='info'>
                        <AlertIcon />        
                        <Text>
                            You have no series to watch, go explore!
                        </Text>
                    </Alert>}
                />
                
            </Stack>
        </FocusContext.Provider>
    </>
}