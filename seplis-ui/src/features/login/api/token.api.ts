import { mutationApiHelper, MutationApiHelperProps } from '@/utils/api-crud'
import { Token, TokenCreate } from '../types/login.types'

interface TokenProps extends MutationApiHelperProps<TokenCreate> {}

export const { mutation: createToken, useMutation: useCreateToken } =
    mutationApiHelper<Token, TokenProps>({
        url: () => '2/token',
        method: 'POST',
    })
