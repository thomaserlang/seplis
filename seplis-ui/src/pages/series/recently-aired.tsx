import MainMenu from '@/components/main-menu'
import SeriesUserList from '@/components/series/user-list'
import { ISeriesAndEpisode } from '@/interfaces/series'
import { episodeNumber, setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function SeriesRecentlyAired() {
    const navigate = useNavigate()
    const location = useLocation()
    useEffect(() => {
        setTitle('Series recently aired')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="series" />
            <Box margin="1rem">
                <SeriesUserList<ISeriesAndEpisode>
                    title="Series recently aired"
                    url="/2/series/recently-aired?user_watchlist=true"
                    parseItem={(item) => ({
                        key: `series-${item.series.id}`,
                        title: item.series.title,
                        img: item.series.poster_image?.url,
                        bottomText: episodeNumber(item.episode),
                    })}
                    onItemSelected={(item: ISeriesAndEpisode) => {
                        navigate(`/series/${item.series.id}`, {
                            state: {
                                background: location,
                            },
                        })
                    }}
                    emptyMessage={`No series on your watchlist has recently aired.`}
                />
            </Box>
        </>
    )
}
