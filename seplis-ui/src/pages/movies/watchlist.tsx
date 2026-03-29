import MainMenu from '@/components/main-menu'
import MovieUserList from '@/components/movie/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function MovieWatchlist() {
    useEffect(() => {
        setTitle('Movie watchlist')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="movies" />
            <Box margin="1rem">
                <MovieUserList
                    title="Movie watchlist"
                    url="/2/movies?user_watchlist=true"
                    defaultSort="user_watchlist_added_at_desc"
                    emptyMessage={`You have no movies in your watchlist.`}
                />
            </Box>
        </>
    )
}
