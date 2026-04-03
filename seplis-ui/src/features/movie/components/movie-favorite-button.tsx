import { FavoriteButton } from '@/components/favorite-button'
import { useActiveUser } from '@/features/user/api/active-user.api'
import { toastError } from '@/utils/toast'
import {
    useCreateMovieFavorite,
    useDeleteMovieFavorite,
    useGetMovieFavorite,
} from '../api/movie-favorite.api'

interface Props {
    movieId: number
}

export function MovieFavoriteButton({ movieId }: Props) {
    const [user] = useActiveUser()
    const create = useCreateMovieFavorite({
        onError: (e) => {
            toastError(e)
        },
    })
    const deleteFavorite = useDeleteMovieFavorite({
        onError: (e) => {
            toastError(e)
        },
    })
    const { data, isLoading } = useGetMovieFavorite({
        movieId,
        options: {
            enabled: !!user,
        },
    })

    const toggleFavorite = () => {
        if (data?.favorite) {
            deleteFavorite.mutate({
                movieId,
            })
        } else {
            create.mutate({
                movieId,
            })
        }
    }

    return (
        <FavoriteButton
            active={!!data?.favorite}
            loading={isLoading || create.isPending || deleteFavorite.isPending}
            onClick={toggleFavorite}
        />
    )
}
