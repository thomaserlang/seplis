import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import SeriesUserList from '@seplis/components/series/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function SeriesWatchlist() {
    useEffect(() => {
        setTitle('Series Watchlist')
    }, [location.pathname])

    return <>
        <MainMenu active="series" />
        <Box margin="1rem">
            <SeriesUserList
                title="Series watchlist"
                url="/2/series?user_watchlist=true"
                defaultSort='user_watchlist_added_at_desc'
                emptyMessage={`You have no series in your watchlist.`}
            />
        </Box>
    </>
}
