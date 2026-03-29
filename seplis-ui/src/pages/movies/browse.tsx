import MainMenu from '@/components/main-menu'
import MovieUserList from '@/components/movie/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function MoviesBrowse() {
    useEffect(() => {
        setTitle('Movies')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="movies" />
            <Box margin="1rem">
                <MovieUserList
                    title="Movies"
                    url="/2/movies"
                    defaultSort="popularity_desc"
                    emptyMessage={`No movies to show.`}
                />
            </Box>
        </>
    )
}
