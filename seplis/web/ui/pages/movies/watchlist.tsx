import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import MovieUserList from '@seplis/components/movie/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function MovieWatchlist() {
    useEffect(() => {
        setTitle('Movie Watchlist')
    }, [])

    return <>
        <MainMenu active="movies" />
        <Box margin="1rem">
            <MovieUserList
                title="Movie watchlist"
                url="/2/movies?user_watchlist=true&sort=user_watchlist_added_at_desc"
            />
        </Box>
    </>
}