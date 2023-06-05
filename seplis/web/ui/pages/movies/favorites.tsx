import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import MovieUserList from '@seplis/components/movie/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function MovieFavorites() {
    useEffect(() => {
        setTitle('Movie favorites')
    }, [])

    return <>
        <MainMenu active="movies" />
        <Box margin="1rem">
            <MovieUserList
                title="Movie favorites"
                url="/2/movies?user_favorites=true&sort=user_favorite_added_at_desc"
                emptyMessage={`You have no movies in your favorites.`}
            />
        </Box>
    </>
}