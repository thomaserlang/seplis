import { Alert, AlertIcon, AlertTitle, Flex, Skeleton } from '@chakra-ui/react'
import { FocusHandler } from '@noriginmedia/norigin-spatial-navigation'
import api from '@seplis/api'
import { IPageCursorResult, IPageCursorTotalResult } from '@seplis/interfaces/page'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useInfiniteQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { ErrorMessageFromResponse } from './error'
import { Card } from './slider'

interface IProps<S = any> {
    title: string
    url: string
    urlParams?: any
    onFocus?: FocusHandler,
    onItemSelected?: (item: S) => void
    parseItem: (item: S) => ISliderItem
}

const SplitWidths = ['75px', '100px', '125px', '150px']

export default function List<S = any>({ title, url, urlParams, onFocus, onItemSelected, parseItem }: IProps) {
    const [error, setError] = useState<JSX.Element>(null)
    const [items, setItems] = useState<ISliderItem[]>([])
    const { isInitialLoading, data } = useInfiniteQuery(['list', title, url, urlParams], async ({ pageParam = null }) => {
        try {
            const r = await api.get<IPageCursorTotalResult<S>>(url, {
                params: {
                    ...urlParams,
                    cursor: pageParam,
                },
            })
            return r.data
        } catch (e) {
            setError(ErrorMessageFromResponse(e))
            return null
        }
    })

    useEffect(() => {
        const items = data?.pages.flatMap((page) => page.items.map((item) => {
            const i = parseItem(item)
            i.data = item
            return i
        })) ?? []
        setItems(items)
    }, [data])

    if (error)
        return <Alert status="error" rounded="md">
            <AlertIcon />
            <AlertTitle>{error}</AlertTitle>
        </Alert>

    return <Flex gap="0.75rem" wrap="wrap">
        {isInitialLoading && <SkeletonCards amount={24} />}

        {!isInitialLoading && items && items.map((item, i) => {
            return <Flex key={item.key} grow="1" basis={SplitWidths}>
                <Card
                    item={item}
                    onFocus={onFocus}
                    onItemSelected={onItemSelected}
                    viewItemIndex={i}
                />
            </Flex>
        })}
        <BlankCards amount={24} />
    </Flex>
}

export function SkeletonCards({ amount }: { amount: number }) {
    return <>
        {[...Array(amount).keys()].map((key) => (
            <Flex key={`skeleton-${key}`} grow="1" basis={SplitWidths} >
                <Skeleton className="poster-container slider-item" rounded="md" width="100%" height="100%" />
            </Flex>
        ))}
    </>
}

export function BlankCards({ amount }: { amount: number }) {
    return <>
        {[...Array(amount).keys()].map((key) => (
            <Flex key={`blank-${key}`} height="0px" grow="1" basis={SplitWidths}></Flex>
        ))}
    </>
}