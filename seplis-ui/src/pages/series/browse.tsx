import MainMenu from '@/components/main-menu'
import SeriesUserList from '@/components/series/user-list'
import { setTitle } from '@/utils'
import { Box } from '@chakra-ui/react'
import { useEffect } from 'react'

export default function Browse() {
    useEffect(() => {
        setTitle('Series')
    }, [location.pathname])

    return (
        <>
            <MainMenu active="series" />
            <Box margin="1rem">
                <SeriesUserList
                    title="Series"
                    url="/2/series"
                    defaultSort="popularity_desc"
                    emptyMessage={`No series to show.`}
                />
            </Box>
        </>
    )
}
