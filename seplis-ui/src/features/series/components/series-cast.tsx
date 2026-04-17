import { CastMemberCard } from '@/components/cast-member-card'
import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { pageItemsFlatten } from '@/utils/api-crud'
import {
    Button,
    Center,
    ScrollArea,
    SimpleGrid,
    StyleProp,
} from '@mantine/core'
import { ReactNode } from 'react'
import { useGetSeriesCast } from '../api/series-cast.api'

interface Props {
    seriesId: number
    maxCast?: number
    title?: ReactNode
    loadMoreButton?: boolean
    cols?: StyleProp<number>
    showTotalEpisodes?: boolean
}

export function SeriesCast({
    seriesId,
    maxCast,
    title,
    loadMoreButton,
    cols = { base: 1, xs: 2, sm: 2, md: 3, lg: 4 },
    showTotalEpisodes,
}: Props) {
    const {
        data,
        isLoading,
        error,
        fetchNextPage,
        isFetchingNextPage,
        hasNextPage,
    } = useGetSeriesCast({
        seriesId,
        params: {
            order_le: maxCast ? 99 : undefined,
            per_page: maxCast ? Math.min(maxCast, 100) : 25,
        },
    })

    const cast = pageItemsFlatten(data)

    return (
        <ScrollArea h="100%" onBottomReached={fetchNextPage}>
            {error && !data && <ErrorBox errorObj={error} />}
            {isLoading && <PageLoader />}
            {cast.length > 0 && title}
            <SimpleGrid
                cols={cols}
                spacing={{ base: '0.65rem', sm: '0.75rem', lg: '0.9rem' }}
            >
                {cast.map((person) => (
                    <CastMemberCard
                        key={person.person.id}
                        castMember={person}
                        showTotalEpisodes={showTotalEpisodes}
                    />
                ))}
            </SimpleGrid>
            {isFetchingNextPage && <PageLoader />}
            {loadMoreButton && !isFetchingNextPage && hasNextPage && (
                <Center mt="1rem">
                    <Button variant="default" onClick={() => fetchNextPage()}>
                        Load more
                    </Button>
                </Center>
            )}
        </ScrollArea>
    )
}
