import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import SeriesUserList from '@seplis/components/series/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function SeriesWatched() {    
    useEffect(() => {
        setTitle('Series Watched')
    }, [])

    return <>
        <MainMenu />
        <Box marginTop="1rem"></Box>
        <SeriesUserList 
            title="Watched {total} series" 
            url="/2/users/me/series-watched"
        />
    </>
}
