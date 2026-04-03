import { langCodeToLang } from '@/utils/language.utils'
import { Flex, Image, Pill, Text } from '@mantine/core'
import { SearchResult } from '../types/search.types'

interface Props {
    item: SearchResult
}

export function SearchResultItem({ item }: Props) {
    return (
        <Flex gap="0.5rem">
            <Image src={item.poster_image?.url} w="3rem" radius="sm" />
            <Flex direction="column" gap="0.15rem" miw="0">
                <Text fw={600} mt="-0.25rem" title={item.title || ''} truncate>
                    {item.title || 'Unknown title'}
                </Text>
                <Flex gap="0.75rem" mt="-0.15rem">
                    {item.release_date && (
                        <Text
                            c="dimmed"
                            size="sm"
                            fw={600}
                            title={item.release_date}
                        >
                            {item.release_date.substring(0, 4)}
                        </Text>
                    )}
                    {item.language && (
                        <Text c="dimmed" size="sm">
                            {langCodeToLang(item.language)}
                        </Text>
                    )}
                    {item.runtime && (
                        <Text c="dimmed" size="sm">
                            {item.runtime} min
                        </Text>
                    )}
                    {item.rating && (
                        <Text c="dimmed" size="sm">
                            {item.rating} IMDb
                        </Text>
                    )}
                </Flex>
                <Flex gap="0.25rem" wrap="wrap">
                    {item.type && (
                        <Pill
                            size="sm"
                            fw={600}
                            c={typeColor({ type: item.type })}
                            style={{ textTransform: 'capitalize' }}
                        >
                            {item.type}
                        </Pill>
                    )}
                    {item.genres?.map((g) => (
                        <Pill key={g.id} size="sm" fw={600}>
                            {g.name}
                        </Pill>
                    ))}
                </Flex>
            </Flex>
        </Flex>
    )
}

function typeColor({ type }: { type: string }) {
    switch (type) {
        case 'movie':
            return 'green'
        case 'series':
            return 'blue'
        default:
            return undefined
    }
}
