import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import SeriesUserList from '@seplis/components/series/user-list'
import { setTitle } from '@seplis/utils'
import { useEffect } from 'react'

export default function SeriesFollowing() {    
    useEffect(() => {
        setTitle('Series Following')
    }, [])

    return <>    
        <MainMenu />
        <Box marginTop="1rem"></Box>
        <SeriesUserList 
            title="Following {total} series" 
            url="/2/users/me/series-following"
        />
    </>
}
