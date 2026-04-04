import { mediaTypes } from '@/features/media-type'
import { langCodeToLang } from '@/utils/language.utils'
import { Flex, Image, Pill, Text } from '@mantine/core'
import cx from 'clsx'
import { forwardRef } from 'react'
import { SearchResult } from '../types/search.types'
import classes from './search-result.module.css'

interface Props {
    item: SearchResult
    isSelected?: boolean
    onClick?: (item: SearchResult) => void
}

export const SearchResultItem = forwardRef<HTMLDivElement, Props>(
    ({ item, isSelected, onClick }, ref) => {
        return (
            <Flex
                ref={ref}
                gap="0.5rem"
                onClick={() => onClick?.(item)}
                className={cx(classes.item, { [classes.selected]: isSelected })}
                style={{ cursor: onClick ? 'pointer' : undefined }}
            >
                {item.poster_image && (
                    <Image
                        src={`${item.poster_image.url}@SX320.webp`}
                        w="3rem"
                        radius="sm"
                    />
                )}
                <Flex direction="column" gap="0.15rem" miw="0">
                    <Text
                        fw={600}
                        mt="-0.25rem"
                        title={item.title || ''}
                        truncate
                    >
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
                                c={mediaTypes[item.type]?.color || 'gray'}
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
    },
)
