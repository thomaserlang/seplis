import { Stack } from '@chakra-ui/react'
import { FocusContext, useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import MainMenu from '@seplis/components/main-menu'
import Slider from '@seplis/components/slider'
import { ISeriesAndEpisode, ISeriesUser } from '@seplis/interfaces/series'
import { dateCountdown, episodeNumber, setTitle } from '@seplis/utils'
import { useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SeriesHome() {
    const { ref, focusKey, focusSelf } = useFocusable()
    const navigate = useNavigate()

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

    return <FocusContext.Provider value={focusKey}>
        <MainMenu />

        <Stack ref={ref} marginTop="0.5rem">

            <Slider<ISeriesUser>
                title="Watched"
                url="/2/users/me/series-watched"
                parseItem={(item) => (
                    {
                        key: `series-${item.series.id}`,
                        title: item.series.title,
                        img: item.series.poster_image?.url,
                        bottomText: episodeNumber(item.last_episode_watched),
                    }
                )}
                onFocus={onRowFocus}
                onItemSelected={(item) => {
                    navigate(`/series/${item.series.id}`)
                }}
            />

            <Slider<ISeriesAndEpisode>
                title="Recently Aired"
                url="/2/users/me/series-recently-aired"
                parseItem={(item) => (
                    {
                        key: `series-${item.series.id}`,
                        title: item.series.title,
                        img: item.series.poster_image?.url,
                        bottomText: episodeNumber(item.episode),
                    }
                )}
                onFocus={onRowFocus}
                onItemSelected={(item) => {
                    navigate(`/series/${item.series.id}`)
                }}
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
                onItemSelected={(item) => {
                    navigate(`/series/${item.series.id}`)
                }}
            />

            <Slider<ISeriesAndEpisode>
                title="Episodes to Watch"
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
                onItemSelected={(item) => {
                    navigate(`/series/${item.series.id}`)
                }}
            />

        </Stack>
    </FocusContext.Provider>

}