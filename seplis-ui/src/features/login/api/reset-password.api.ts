import { mutationApiHelper, MutationApiHelperProps } from '@/utils/api-crud'
import {
    RequestResetPasswordCreate,
    ResetPasswordCreate,
} from '../types/reset-password.types'

interface ResetPasswordCreateProps extends MutationApiHelperProps<RequestResetPasswordCreate> {}

export const {
    mutation: createRequestResetPassword,
    useMutation: useCreateRequestResetPassword,
} = mutationApiHelper<void, ResetPasswordCreateProps>({
    url: () => '2/users/send-reset-password',
    method: 'POST',
})

interface ResetPasswordProps extends MutationApiHelperProps<ResetPasswordCreate> {}

export const { mutation: resetPassword, useMutation: useResetPassword } =
    mutationApiHelper<void, ResetPasswordProps>({
        url: () => '2/users/reset-password',
        method: 'POST',
    })
