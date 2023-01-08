import SliderSeriesFollowing from "@seplis/components/slider-series-following"
import SliderRecentlyWatched from "@seplis/components/slider-recently-watched"
import { Stack } from "@chakra-ui/react"
import { useEffect } from "react"

export default function Home() {
    useEffect(() => {
        document.title = 'Home | SEPLIS'
    }, [])
    
    return <Stack spacing={6}>
        <SliderRecentlyWatched />
        <SliderSeriesFollowing />
    </Stack>
}