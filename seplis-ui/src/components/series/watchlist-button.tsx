import api from '@/api'
import { ISeriesWatchlist } from '@/interfaces/series'
import { focusedBorder } from '@/styles'
import { isAuthed } from '@/utils'
import { Button, useToast } from '@chakra-ui/react'
import { useFocusable } from '@noriginmedia/norigin-spatial-navigation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FaBookmark } from 'react-icons/fa'
import { ErrorMessageFromResponse } from '../error'

export default function WatchlistButton({ seriesId }: { seriesId: number }) {
    const toast = useToast()
    const queryClient = useQueryClient()

    const toggleWatchlist = useMutation(
        async (watchlist: boolean) => {
            await queryClient.cancelQueries([
                'series',
                'watchlist-button',
                seriesId,
            ])
            if (watchlist) {
                await api.delete(`/2/series/${seriesId}/watchlist`)
            } else {
                await api.put(`/2/series/${seriesId}/watchlist`)
            }
            queryClient.setQueryData(['series', 'watchlist-button', seriesId], {
                on_watchlist: !watchlist,
            })
        },
        {
            onError: (e) => {
                toast({
                    title: ErrorMessageFromResponse(e),
                    status: 'error',
                    isClosable: true,
                    position: 'top',
                })
            },
        },
    )

    const { isInitialLoading, data } = useQuery(
        ['series', 'watchlist-button', seriesId],
        async () => {
            const result = await api.get<ISeriesWatchlist>(
                `/2/series/${seriesId}/watchlist`,
            )
            return result.data
        },
        {
            enabled: isAuthed(),
        },
    )

    const handleClick = () => {
        toggleWatchlist.mutate(data?.on_watchlist ?? false)
    }

    const { ref, focused } = useFocusable({
        onEnterPress: () => handleClick,
    })

    return (
        <Button
            ref={ref}
            isLoading={isInitialLoading || toggleWatchlist.isLoading}
            colorScheme={data?.on_watchlist ? 'yellow' : undefined}
            onClick={handleClick}
            leftIcon={<FaBookmark />}
            style={focused ? focusedBorder : undefined}
        >
            Watchlist
        </Button>
    )
}
