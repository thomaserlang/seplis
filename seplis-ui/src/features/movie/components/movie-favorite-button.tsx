import {
    FavoriteButton,
    FavoriteButtonProps,
} from '@/components/favorite-button'
import { useActiveUser } from '@/features/user/api/session.store'
import { toastError } from '@/utils/toast'
import {
    useCreateMovieFavorite,
    useDeleteMovieFavorite,
    useGetMovieFavorite,
} from '../api/movie-favorite.api'

interface Props extends FavoriteButtonProps {
    movieId: number
}

export function MovieFavoriteButton({ movieId, ...props }: Props) {
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
            {...props}
        />
    )
}
