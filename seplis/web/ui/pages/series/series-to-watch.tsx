import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import SeriesUserList from '@seplis/components/series/user-list'
import { ISeriesAndEpisode } from '@seplis/interfaces/series'
import { episodeNumber, setTitle } from '@seplis/utils'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function SeriesToWatch() {
    const navigate = useNavigate()
    const location = useLocation()
    useEffect(() => {
        setTitle('Series to Watch')
    }, [])

    return <>
        <MainMenu active="series" />
        <Box margin="1rem">
            <SeriesUserList<ISeriesAndEpisode>
                title="Series to watch"
                url="/2/users/me/series-to-watch?user_can_watch=true"
                parseItem={(item) => (
                    {
                        key: `series-${item.series.id}`,
                        title: item.series.title,
                        img: item.series.poster_image?.url,
                        bottomText: episodeNumber(item.episode),
                    }
                )}
                onItemSelected={(item: ISeriesAndEpisode) => {
                    navigate(`/series/${item.series.id}`, {state: {
                        background: location
                    }})
                }}
            />
        </Box>
    </>
}