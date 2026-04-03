import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Text } from '@mantine/core'
import { useGetSearch } from '../api/search.api'
import { SearchResultItem } from './search-result'

interface Props {
    query: string
}

export function SearchResults({ query }: Props) {
    const { data, isLoading, error } = useGetSearch({
        params: {
            query,
        },
        options: {
            enabled: !!query,
        },
    })

    if (error) return <ErrorBox errorObj={error} />
    if (isLoading) return <PageLoader />
    if (!query) return null
    if (!data)
        return (
            <Text fw={600} size="lg">
                No results
            </Text>
        )

    return data.map((result) => (
        <SearchResultItem key={result.id} item={result} />
    ))
}
