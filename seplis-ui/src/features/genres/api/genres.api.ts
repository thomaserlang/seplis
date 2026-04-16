import { Genre } from '@/features/genres/types/genre.types'
import { MediaType } from '@/features/media-type'
import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'

interface Params {
    type: MediaType
}

interface GetProps extends ApiHelperProps<Params> {}

export const { get: getGenres, useGet: useGetGenres } = useApiHelper<
    Genre[],
    GetProps
>({
    url: () => '/2/genres',
    queryKey: ({ params }) => ['genres', params!.type],
})
