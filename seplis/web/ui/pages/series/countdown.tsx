import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import SeriesUserList from '@seplis/components/series/user-list'
import { ISeriesAndEpisode } from '@seplis/interfaces/series'
import { dateCountdown, episodeNumber, setTitle } from '@seplis/utils'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function SeriesCountdown() {
    const navigate = useNavigate()
    const location = useLocation()
    useEffect(() => {
        setTitle('Series countdown')
    }, [location.pathname])

    return <>
        <MainMenu active="series" />
        <Box margin="1rem">
            <SeriesUserList<ISeriesAndEpisode>
                title="Series countdown"
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
                onItemSelected={(item: ISeriesAndEpisode) => {
                    navigate(`/series/${item.series.id}`, {state: {
                        background: location
                    }})
                }}
                emptyMessage={`No series on your watchlist has episodes airing in the future.`}
                showFilterButton={false}
            />
        </Box>
    </>
}