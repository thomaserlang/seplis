import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { UserWatched } from '../types/user-watched.types'

interface Params {
    user_can_watch: boolean
}

interface GetProps extends ApiHelperProps<Params> {}

export const {
    getPage: getUserWatched,
    useGetPage: useGetUserWatched,
    queryKey: getUserWatchedQueryKey,
} = usePageApiHelper<UserWatched, GetProps>({
    url: () => '/2/users/me/watched',
    queryKey: () => ['user', 'watched'],
})
