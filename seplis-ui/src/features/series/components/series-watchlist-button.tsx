import { WatchlistButton } from '@/components/watchlist-button'
import { useActiveUser } from '@/features/user/api/active-user.api'
import { toastError } from '@/utils/toast'
import {
    useCreateSeriesWatchlist,
    useDeleteSeriesWatchlist,
    useGetSeriesWatchlist,
} from '../api/series-watchlist.api'

interface Props {
    seriesId: number
}

export function SeriesWatchlistButton({ seriesId }: Props) {
    const [user] = useActiveUser()
    const create = useCreateSeriesWatchlist({
        onError: (e) => {
            toastError(e)
        },
    })
    const deleteWatchlist = useDeleteSeriesWatchlist({
        onError: (e) => {
            toastError(e)
        },
    })
    const { data, isLoading } = useGetSeriesWatchlist({
        seriesId,
        options: {
            enabled: !!user,
        },
    })

    const toggleWatchlist = () => {
        if (data?.on_watchlist) {
            deleteWatchlist.mutate({
                seriesId,
            })
        } else {
            create.mutate({
                seriesId,
            })
        }
    }

    return (
        <WatchlistButton
            active={!!data?.on_watchlist}
            loading={isLoading || create.isPending || deleteWatchlist.isPending}
            onClick={() => {
                toggleWatchlist()
            }}
        />
    )
}
