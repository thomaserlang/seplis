import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import MovieUserList from '@seplis/components/movie/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function MoviesWatched() {
    useEffect(() => {
        setTitle('Movies Watched')
    }, [])

    return <>
        <MainMenu />
        <Box margin="1rem">
            <MovieUserList
                title="Watched {total} movies"
                url="/2/users/me/movies-watched"
            />
        </Box>
    </>
}
