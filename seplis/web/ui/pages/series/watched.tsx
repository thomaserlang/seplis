import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import UserSeriesList from '@seplis/components/series/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function SeriesWatched() {
    useEffect(() => {
        setTitle('Series watched')
    }, [])

    return <>
        <MainMenu active="series" />
        <Box margin="1rem">
            <UserSeriesList
                title="Series watched"
                url="/2/series?user_has_watched=true"
                defaultSort='user_last_episode_watched_at_desc'
                emptyMessage={`You have not watched any series.`}
            />
        </Box>
    </>
}
