import { Heading, SimpleGrid, Stack, Text } from '@chakra-ui/react'
import api from '@seplis/api'
import { IPageCursorResult } from '@seplis/interfaces/page'
import { ISeriesCastPerson } from '@seplis/interfaces/series-cast'
import { useQuery } from '@tanstack/react-query'
import CastCard, { CastCardSkeleton } from './cast-card'

export default function CastFeatured({ seriesId }: { seriesId: number }) {
    const { isInitialLoading, data } = useQuery(['movie', seriesId, 'featured'], async () => {
        const result = await api.get<IPageCursorResult<ISeriesCastPerson>>(`/2/series/${seriesId}/cast`, {
            params: {
                per_page: 12,
                order_le: 99,
            },
        })
        return result.data
    })
    return <Stack spacing="0.5rem">
        <Heading fontSize="2xl" fontWeight="600">Top cast</Heading>
        <SimpleGrid minChildWidth={'300px'} spacing="0.5rem">
            {isInitialLoading ? [...Array(3)].map((_, i) => (
                <CastCardSkeleton key={i} />
            )) : data.items.length > 0 ? data.items.map(member => (
                <CastCard key={member.person.id} castPerson={member} />
            )) : <Text>No cast specified.</Text>}
        </SimpleGrid>
    </Stack>
}