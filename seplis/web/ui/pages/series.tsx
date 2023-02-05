import { Box } from "@chakra-ui/react"
import api from "@seplis/api"
import Series from "@seplis/components/series/series"
import SeriesSkeleton from "@seplis/components/series/skeleton"
import { ISeries } from "@seplis/interfaces/series"
import { setTitle } from "@seplis/utils"
import { useQuery } from "@tanstack/react-query"
import { useParams } from "react-router-dom"


export default function SeriesPage() {    
    const { seriesId } = useParams()    
    const { isInitialLoading, data } = useQuery<ISeries>(['series', seriesId], async () => {
        const data = await api.get<ISeries>(`/2/series/${seriesId}`)
        setTitle(data.data.title)
        return data.data
    })

    return <Box margin="1rem">
        {isInitialLoading ? <SeriesSkeleton /> : <Series series={data} />}
    </Box>
}