import MainMenu from '@/components/main-menu'
import MovieUserList from '@/components/movie/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function MovieFavorites() {
    useEffect(() => {
        setTitle('Movie favorites')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="movies" />
            <Box margin="1rem">
                <MovieUserList
                    title="Movie favorites"
                    url="/2/movies?user_favorites=true"
                    defaultSort="user_favorite_added_at_desc"
                    emptyMessage={`You have no movies in your favorites.`}
                />
            </Box>
        </>
    )
}
