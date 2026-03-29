import MainMenu from '@/components/main-menu'
import MovieUserList from '@/components/movie/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function MoviesWatched() {
    useEffect(() => {
        setTitle('Movies watched')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="movies" />
            <Box margin="1rem">
                <MovieUserList
                    title="Movies watched"
                    url="/2/movies?user_has_watched=true"
                    defaultSort="user_last_watched_at_desc"
                    emptyMessage={`You have not watched any movies.`}
                />
            </Box>
        </>
    )
}
