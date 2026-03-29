import MainMenu from '@/components/main-menu'
import SeriesUserList from '@/components/series/user-list'
import { ISeriesAndEpisode } from '@/interfaces/series'
import { episodeNumber, setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function SeriesToWatch() {
    const navigate = useNavigate()
    const location = useLocation()
    useEffect(() => {
        setTitle('Series to watch')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="series" />
            <Box margin="1rem">
                <SeriesUserList<ISeriesAndEpisode>
                    title="Series to watch"
                    url="/2/series/to-watch"
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
                    emptyMessage={`You have no series to watch.`}
                />
            </Box>
        </>
    )
}
