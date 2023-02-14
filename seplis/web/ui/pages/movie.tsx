import api from "@seplis/api"
import { IMovie } from "@seplis/interfaces/movie"
import { setTitle } from "@seplis/utils"
import { useQuery } from "@tanstack/react-query"
import { useParams } from "react-router-dom"
import Movie from "@seplis/components/movie/movie"
import { Box } from "@chakra-ui/react"
import { MovieSkeleton } from "@seplis/components/movie/skeleton"
import MainMenu from "@seplis/components/main-menu"


export default function MoviePage() {
    const { movieId } = useParams()
    const { isInitialLoading, data } = useQuery<IMovie>(['movie', movieId], async () => {
        const data = await api.get<IMovie>(`/2/movies/${movieId}`)
        setTitle(data.data.title)
        return data.data
    })

    return <>
        <MainMenu />
        <Box margin="1rem">
            {isInitialLoading ? <MovieSkeleton /> : <Movie movie={data} />}
        </Box>
    </>
}

