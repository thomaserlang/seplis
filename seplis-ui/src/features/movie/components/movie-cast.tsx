import { CastMemberCard } from '@/components/cast-member-card'
import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { pageItemsFlatten } from '@/utils/api-crud'
import { Button, Center, ScrollArea, SimpleGrid } from '@mantine/core'
import { ReactNode } from 'react'
import { useGetMovieCast } from '../api/movie-cast.api'

interface Props {
    movieId: number
    maxCast?: number
    title?: ReactNode
    loadMoreButton?: boolean
}

export function MovieCast({ movieId, maxCast, title, loadMoreButton }: Props) {
    const {
        data,
        isLoading,
        error,
        fetchNextPage,
        isFetchingNextPage,
        hasNextPage,
    } = useGetMovieCast({
        movieId,
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
                cols={{ base: 3, xs: 4, sm: 5, md: 6, lg: 7 }}
                spacing="0.5rem"
            >
                {cast.map((person) => (
                    <CastMemberCard
                        key={person.person.id}
                        castMember={person}
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
