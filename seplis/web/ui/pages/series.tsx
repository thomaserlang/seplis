import { Box } from '@chakra-ui/react'
import MainMenu from '@seplis/components/main-menu'
import { SeriesLoad } from '@seplis/components/series/series'
import { useParams } from 'react-router-dom'


export default function SeriesPage() {    
    const { seriesId } = useParams()

    return <>
        <MainMenu />
        <Box margin='1rem'>
            <SeriesLoad seriesId={parseInt(seriesId)} />
        </Box>
    </>
}