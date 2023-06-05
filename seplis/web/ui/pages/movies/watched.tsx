import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import MovieUserList from '@seplis/components/movie/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function MoviesWatched() {
    useEffect(() => {
        setTitle('Movies watched')
    }, [])

    return <>
        <MainMenu active="movies" />
        <Box margin="1rem">
            <MovieUserList
                title="Movies watched"
                url="/2/movies?user_has_watched=true&sort=user_last_watched_at_desc"
                emptyMessage={`You have not watched any movies.`}
            />
        </Box>
    </>
}
