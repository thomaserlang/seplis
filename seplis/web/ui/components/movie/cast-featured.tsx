import { Heading, SimpleGrid, Stack, Text } from '@chakra-ui/react'
import api from '@seplis/api'
import { IMovieCastPerson } from '@seplis/interfaces/movie-cast'
import { IPageCursorResult } from '@seplis/interfaces/page'
import { useQuery } from '@tanstack/react-query'
import CastCard, { CastCardSkeleton } from './cast-card'

export default function CastFeatured({ movieId }: { movieId: number }) {
    const { isInitialLoading, data } = useQuery(['movie', movieId, 'featured'], async () => {
        const result = await api.get<IPageCursorResult<IMovieCastPerson>>(`/2/movies/${movieId}/cast`, {
            params: {
                per_page: 12,
                order_le: 100,
            },
        })
        return result.data
    })
    return <Stack spacing="0.5rem">
        <Heading as="h2" size="md" fontWeight="600">Top cast</Heading>

        <SimpleGrid minChildWidth={'300px'} spacing="0.5rem">
            {isInitialLoading ? [...Array(3)].map((_, i) => (
                <CastCardSkeleton key={i} />
            )) : data?.items.length > 0 ? data?.items.map(member => (
                <CastCard key={member.person.id} castPerson={member} />
            )) : <Text>No cast specified.</Text>}
        </SimpleGrid>
    </Stack>
}