import {
    ApiHelperProps,
    mutationApiHelper,
    MutationApiHelperProps,
    useApiHelper,
} from '@/utils/api-crud'
import { User, UserCreate } from '../types/user.types'

interface CurrentUserProps extends ApiHelperProps {}

export const {
    get: getCurrentUser,
    useGet: useGetCurrentUser,
    queryKey: currentUserQueryKey,
} = useApiHelper<User, CurrentUserProps>({
    url: () => '2/users/me',
    queryKey: () => ['current-user'],
})

interface CreateUserProps extends MutationApiHelperProps<UserCreate> {}

export const { mutation: createUser, useMutation: useCreateUser } =
    mutationApiHelper<User, CreateUserProps>({
        url: () => '2/users',
        method: 'POST',
    })
