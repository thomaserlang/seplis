import MainMenu from '@/components/main-menu'
import SeriesUserList from '@/components/series/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function SeriesWatchlist() {
    useEffect(() => {
        setTitle('Series Watchlist')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="series" />
            <Box margin="1rem">
                <SeriesUserList
                    title="Series watchlist"
                    url="/2/series?user_watchlist=true"
                    defaultSort="user_watchlist_added_at_desc"
                    emptyMessage={`You have no series in your watchlist.`}
                />
            </Box>
        </>
    )
}
