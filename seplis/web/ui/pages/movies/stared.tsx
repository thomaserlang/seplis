import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import MovieUserList from '@seplis/components/movie/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function MoviesStared() {
    useEffect(() => {
        setTitle('Movies Stared')
    }, [])

    return <>
        <MainMenu active="movies" />
        <Box margin="1rem">
            <MovieUserList
                title="Movies Stared"
                url="/2/movies?user_stared=true&sort=user_stared_at_desc"
            />
        </Box>
    </>
}
