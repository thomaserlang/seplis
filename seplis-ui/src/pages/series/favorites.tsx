import MainMenu from '@/components/main-menu'
import SeriesUserList from '@/components/series/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function SeriesFavorites() {
    useEffect(() => {
        setTitle('Series favorites')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="series" />
            <Box margin="1rem">
                <SeriesUserList
                    title="Series favorites"
                    url="/2/series?user_favorites=true"
                    defaultSort="user_favorite_added_at_desc"
                    emptyMessage={`You have no series in your favorites.`}
                />
            </Box>
        </>
    )
}
