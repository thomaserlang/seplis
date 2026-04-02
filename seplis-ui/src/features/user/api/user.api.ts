import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { User } from '../types/user.types'

interface CurrentUserProps extends ApiHelperProps {}

export const {
    get: getCurrentUser,
    useGet: useGetCurrentUser,
    queryKey: currentUserQueryKey,
} = useApiHelper<User, CurrentUserProps>({
    url: () => '2/users/me',
    queryKey: () => ['current-user'],
})
