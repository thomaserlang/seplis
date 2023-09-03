import { Text, Alert, AlertIcon, AlertTitle, Box, Button, Drawer, DrawerBody, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay, Flex, Heading, Skeleton, useDisclosure, AlertDescription } from '@chakra-ui/react'
import { FocusHandler } from '@noriginmedia/norigin-spatial-navigation'
import api from '@seplis/api'
import { IPageCursorTotalResult } from '@seplis/interfaces/page'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useInfiniteQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { FaFilter } from 'react-icons/fa'
import { ErrorMessageFromResponse } from './error'
import { Card } from './slider'
import { removeEmpty } from '../utils'

interface IProps<S = any> {
    title: string
    url: string
    urlParams?: Object
    emptyMessage?: string | null,
    filtersActive?: boolean,
    onFocus?: FocusHandler,
    onItemSelected?: (item: S) => void
    parseItem: (item: S) => ISliderItem
    renderFilter?: TRenderFilter
}

type TRenderFilter = (options?: {
    onClose: () => void
}) => JSX.Element

const SplitWidths = ['100px', '125px', null, '175px', null, '200px']

export default function List<S = any>({ 
    title, 
    url, 
    urlParams,
    emptyMessage,
    filtersActive = false,
    renderFilter, 
    onFocus, 
    onItemSelected, 
    parseItem
}: IProps) {
    const [items, setItems] = useState<ISliderItem[]>([])
    const { isFetching, isInitialLoading, data, error, fetchNextPage, isFetchingNextPage, hasNextPage } = useInfiniteQuery(['list', title, url, urlParams], async ({ pageParam = null }) => {
        const r = await api.get<IPageCursorTotalResult<S>>(url, {
            params: {
                ...removeEmpty(urlParams),
                cursor: pageParam,
            },
        })
        return r.data
    }, {
        getNextPageParam: (lastPage) => lastPage.cursor ?? undefined,
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
            <AlertTitle>{ErrorMessageFromResponse(error)}</AlertTitle>
        </Alert>
    const loading = (isInitialLoading || isFetchingNextPage || (isFetching && data?.pages?.length == 1))
    return <>
        <Flex wrap="wrap">
            <Heading as="h1" marginBottom="1rem" fontSize={['1.5rem', '2rem']}>{title.replace('{total}', data?.pages?.[0]?.total?.toString() || '...')}</Heading>
            <Box marginLeft="auto"><FilterButton renderFilter={renderFilter} /></Box>
        </Flex>
        
        {!loading && items.length == 0 && data?.pages[0]?.items?.length == 0 && emptyMessage && <Alert status='info' variant='top-accent'>
            <AlertIcon /> 
            <AlertTitle>{emptyMessage}</AlertTitle>
            {filtersActive && <AlertDescription>
                You have filters active!
            </AlertDescription>}
        </Alert>}

        <Flex gap="0.75rem" wrap="wrap">
            {(isFetchingNextPage || !loading) && items && items.map((item, i) => {
                return <Flex key={item.key} grow="1" basis={SplitWidths}>
                    <Card
                        item={item}
                        onFocus={onFocus}
                        onItemSelected={onItemSelected}
                        viewItemIndex={i}
                    />
                </Flex>
            })}
            {loading && <SkeletonCards amount={24} />}
            <BlankCards amount={12} />
        </Flex>

        {hasNextPage && <Flex marginBottom="2rem" alignItems="center" justifyContent="center">
            <Button onClick={() => fetchNextPage()} size="lg">Load more</Button>
        </Flex>}
    </>
}


function SkeletonCards({ amount }: { amount: number }) {
    return <>
        {[...Array(amount).keys()].map((key) => (
            <Flex key={`skeleton-${key}`} grow="1" basis={SplitWidths} >
                <Skeleton className="poster-container" rounded="md" width="100%" height="100%" />
            </Flex>
        ))}
    </>
}


function BlankCards({ amount }: { amount: number }) {
    return <>
        {[...Array(amount).keys()].map((key) => (
            <Flex key={`blank-${key}`} height="0px" grow="1" basis={SplitWidths}></Flex>
        ))}
    </>
}


function FilterButton({ renderFilter }: { renderFilter: TRenderFilter }) {
    const { isOpen, onOpen, onClose } = useDisclosure()
    return <>
        <Button colorScheme="blue" rightIcon={<FaFilter />} onClick={onOpen}>Filter</Button>
        <Drawer
            isOpen={isOpen}
            placement='right'
            onClose={onClose}
        >
            <DrawerOverlay />
            <DrawerContent>
                <DrawerCloseButton />
                <DrawerHeader>Filter</DrawerHeader>

                <DrawerBody>
                    {renderFilter({
                        onClose: onClose,
                    })}
                </DrawerBody>
            </DrawerContent>
        </Drawer>
    </>
}