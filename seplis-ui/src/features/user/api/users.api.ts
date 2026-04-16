import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { UserPublic } from '../types/user.types'

interface UsersGetParams {
    username: string
}

interface UsersGetProps extends ApiHelperProps<UsersGetParams> {}

export const {
    get: getUsers,
    useGet: useGetUsers,
    queryKey: usersQueryKey,
} = useApiHelper<UserPublic[], UsersGetProps>({
    url: () => '2/users',
    queryKey: ({ params }) => ['users', params?.username],
})
