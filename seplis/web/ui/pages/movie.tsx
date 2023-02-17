import { setTitle } from "@seplis/utils"
import { useParams } from "react-router-dom"
import { MovieLoad } from "@seplis/components/movie/movie"
import { Box } from "@chakra-ui/react"
import MainMenu from "@seplis/components/main-menu"


export default function MoviePage() {
    const { movieId } = useParams()

    return <>
        <MainMenu />
        <Box margin="1rem">
            <MovieLoad movieId={parseInt(movieId)} onLoaded={(movie) => {
                setTitle(movie.title)
            }} />
        </Box>
    </>
}

