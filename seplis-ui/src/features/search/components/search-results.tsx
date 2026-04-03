import { Flex, ScrollArea } from '@mantine/core'
import { useEffect, useRef } from 'react'
import { SearchResult } from '../types/search.types'
import { SearchResultItem } from './search-result'

interface Props {
    results: SearchResult[]
    selectedIndex?: number
    onSelected?: (item: SearchResult) => void
}

export function SearchResults({ results, selectedIndex, onSelected }: Props) {
    const itemRefs = useRef<(HTMLDivElement | null)[]>([])

    useEffect(() => {
        if (selectedIndex == null || selectedIndex < 0) return
        const el = itemRefs.current[selectedIndex]
        if (!el) return
        el.scrollIntoView({ block: 'nearest' })
    }, [selectedIndex])

    return (
        <ScrollArea.Autosize mah={400}>
            <Flex direction="column" gap="0.25rem" h="100%">
                {results.map((result, index) => (
                    <SearchResultItem
                        key={result.id}
                        ref={(el) => {
                            itemRefs.current[index] = el
                        }}
                        item={result}
                        isSelected={index === selectedIndex}
                        onClick={onSelected}
                    />
                ))}
            </Flex>
        </ScrollArea.Autosize>
    )
}
