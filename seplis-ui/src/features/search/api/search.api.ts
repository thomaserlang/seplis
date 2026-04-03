import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { SearchResult } from '../types/search.types'

interface SearchParams {
    query: string | undefined
}

interface SearchProps extends ApiHelperProps<SearchParams> {}

export const {
    get: getSearch,
    useGet: useGetSearch,
    queryKey: searchQueryKey,
} = useApiHelper<SearchResult[], SearchProps>({
    url: () => `2/search`,
    queryKey: ({ params }) => ['search', params].filter((f) => f !== undefined),
})
