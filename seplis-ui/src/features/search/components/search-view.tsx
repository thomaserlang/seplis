import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Flex, Text, TextInput } from '@mantine/core'
import { useField } from '@mantine/form'
import { useHotkeys } from '@mantine/hooks'
import { useState } from 'react'
import { useGetSearch } from '../api/search.api'
import { SearchResult } from '../types/search.types'
import { SearchResults } from './search-results'

interface Props {
    onSelected?: (item: SearchResult) => void
}

export function SearchView({ onSelected }: Props) {
    const field = useField({
        mode: 'controlled',
        initialValue: '',
    })

    const { data, isLoading, error } = useGetSearch({
        params: {
            query: field.getValue(),
        },
        options: {
            enabled: !!field.getValue(),
        },
    })

    useHotkeys(
        [
            [
                'ArrowUp',
                () => {
                    setSelectedIndex((i) => Math.max(i - 1, 0))
                },
            ],
            [
                'ArrowDown',
                () => {
                    const count = data?.length ?? 0
                    setSelectedIndex((i) => Math.min(i + 1, count - 1))
                },
            ],
            [
                'Enter',
                () => {
                    if (selectedIndex >= 0 && data && data[selectedIndex]) {
                        onSelected?.(data[selectedIndex])
                    }
                },
            ],
        ],
        [],
    )

    const [selectedIndex, setSelectedIndex] = useState<number>(-1)

    return (
        <Flex direction="column" gap="1rem">
            <TextInput
                placeholder="Search..."
                size="lg"
                data-autofocus
                {...field.getInputProps()}
                onChange={(e) => {
                    field.getInputProps().onChange(e)
                    setSelectedIndex(0)
                }}
            />

            {error && <ErrorBox errorObj={error} />}
            {isLoading && <PageLoader />}

            {!data && field.getValue() && !isLoading && (
                <Text fw={600} size="lg">
                    No results
                </Text>
            )}
            {data && !isLoading && (
                <SearchResults
                    query={field.getValue()}
                    results={data}
                    selectedIndex={selectedIndex}
                    onSelected={onSelected}
                />
            )}
        </Flex>
    )
}
