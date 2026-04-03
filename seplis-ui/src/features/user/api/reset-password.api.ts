import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'
import {
    RequestResetPasswordCreate,
    ResetPasswordCreate,
} from '../types/reset-password.types'

interface ResetPasswordCreateProps extends MutationApiHelperProps<RequestResetPasswordCreate> {}

export const {
    mutation: createRequestResetPassword,
    useMutation: useCreateRequestResetPassword,
} = useMutationApiHelper<void, ResetPasswordCreateProps>({
    url: () => '2/users/send-reset-password',
    method: 'POST',
})

interface ResetPasswordProps extends MutationApiHelperProps<ResetPasswordCreate> {}

export const { mutation: resetPassword, useMutation: useResetPassword } =
    useMutationApiHelper<void, ResetPasswordProps>({
        url: () => '2/users/reset-password',
        method: 'POST',
    })
