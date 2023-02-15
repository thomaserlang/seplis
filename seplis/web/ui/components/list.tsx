import { Alert, AlertIcon, AlertTitle, Flex, Skeleton } from '@chakra-ui/react'
import { FocusHandler } from '@noriginmedia/norigin-spatial-navigation'
import api from '@seplis/api'
import { IPageResult } from '@seplis/interfaces/page'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
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
    const { isInitialLoading, data } = useQuery(['list', title, url, urlParams], async () => {
        try {
            const r = await api.get<IPageResult<S>>(url, {
                params: urlParams,
            })
            return r.data
        } catch (e) {
            setError(ErrorMessageFromResponse(e))
            return null
        }
    })

    if (error)
        return <Alert status="error" rounded="md">
            <AlertIcon />
            <AlertTitle>{error}</AlertTitle>
        </Alert>

    return <Flex gap="0.75rem" wrap="wrap">
        {isInitialLoading && <SkeletonCards amount={24} />}

        {!isInitialLoading && data && data.items.map((item, i) => {
            const p = parseItem(item)
            p.data = item
            return <Flex key={p.key} grow="1" basis={SplitWidths}>
                <Card
                    item={p}
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