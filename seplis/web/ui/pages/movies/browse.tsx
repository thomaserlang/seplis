import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import MovieUserList from '@seplis/components/movie/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function MoviesBrowse() {
    useEffect(() => {
        setTitle('Movies')
    }, [location.pathname])

    return <>
        <MainMenu active="movies" />
        <Box margin="1rem">
            <MovieUserList
                title="Movies"
                url="/2/movies"
                defaultSort='popularity_desc'
                emptyMessage={`No movies to show.`}
            />
        </Box>
    </>
}
