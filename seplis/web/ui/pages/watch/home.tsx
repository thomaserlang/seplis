import { Stack } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { ISeries, ISeriesAndEpisode } from '@seplis/interfaces/series'
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
        navigate(`/series/${item.series.id}`, {state: {
            background: location
        }})
    }, [])

    const seriesSelected = useCallback((series: ISeries) => {
        navigate(`/series/${series.id}`, {state: {
            background: location
        }})
    }, [])

    return <>
        <MainMenu />
        
        <FocusContext.Provider value={focusKey}>

            <Stack ref={ref} marginTop="0.5rem" marginBottom="0.5rem">

                <Slider<ISeriesAndEpisode>
                    title="Series to Watch"
                    url="/2/users/me/series-to-watch?can_watch=true"
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
                />

<               Slider<ISeries>
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
                />


            </Stack>
        </FocusContext.Provider>
    </>
}