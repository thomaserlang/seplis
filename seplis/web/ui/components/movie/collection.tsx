import { Box, Flex, Heading, Stack, Wrap, WrapItem } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovie } from '@seplis/interfaces/movie'
import { IMovieCollection } from '@seplis/interfaces/movie-collection'
import { IPageCursorResult } from '@seplis/interfaces/page'
import { useQuery } from '@tanstack/react-query'
import { useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { PosterAspectRatio } from '../poster'

export default function MovieCollection({ collection }: { collection: IMovieCollection }) {
    const navigate = useNavigate()
    const location = useLocation()
    const selected = useCallback((movie: IMovie) => {
        navigate(`/movies/${movie.id}`, { state: { background: location.state?.background || location } })
    }, [])

    const { data, isLoading } = useQuery(['movie-collection', collection.id], async () => {
        const r = await api.get<IPageCursorResult<IMovie>>('/2/movies', {
            params: {
                collection_id: collection.id,
                sort: 'release_date_asc',
                per_page: 100,
            }
        })
        return r.data
    })
    if (isLoading)
        return null
    return <Stack>
        <Heading fontSize="2xl" fontWeight="600">{collection.name}</Heading>
        <Wrap>        
            {data.items.map((r) => <Flex key={r.id} basis="120px"><WrapItem width="100%">
                <PosterAspectRatio
                    url={`${r.poster_image?.url}@SX320.webp`} 
                    title={r.title}
                    onClick={() => {
                        selected(r)
                    }}
                /></WrapItem>
            </Flex>)}
        </Wrap>
    </Stack>
}