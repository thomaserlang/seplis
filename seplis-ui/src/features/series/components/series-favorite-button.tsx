import { FavoriteButton } from '@/components/favorite-button'
import { WatchlistButtonProps } from '@/components/watchlist-button'
import { useActiveUser } from '@/features/user/api/session.store'
import { toastError } from '@/utils/toast'
import {
    useCreateSeriesFavorite,
    useDeleteSeriesFavorite,
    useGetSeriesFavorite,
} from '../api/series-favorite.api'

interface Props extends Partial<WatchlistButtonProps> {
    seriesId: number
}

export function SeriesFavoriteButton({ seriesId, ...props }: Props) {
    const [user] = useActiveUser()
    const create = useCreateSeriesFavorite({
        onError: (e) => {
            toastError(e)
        },
    })
    const deleteFavorite = useDeleteSeriesFavorite({
        onError: (e) => {
            toastError(e)
        },
    })
    const { data, isLoading } = useGetSeriesFavorite({
        seriesId,
        options: {
            enabled: !!user,
        },
    })

    const toggleFavorite = () => {
        if (data?.favorite) {
            deleteFavorite.mutate({
                seriesId,
            })
        } else {
            create.mutate({
                seriesId,
            })
        }
    }

    return (
        <FavoriteButton
            active={!!data?.favorite}
            loading={isLoading || create.isPending || deleteFavorite.isPending}
            onClick={toggleFavorite}
            {...props}
        />
    )
}
