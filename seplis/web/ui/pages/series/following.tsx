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
        <Box margin="1rem">
            <SeriesUserList
                title="Series Following"
                url="/2/series?user_following=true"
                defaultSort='user_followed_at_desc'
            />
        </Box>
    </>
}
