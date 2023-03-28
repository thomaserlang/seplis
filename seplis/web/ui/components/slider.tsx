import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons'
import { Box, Flex, Heading, HStack, Image, Skeleton } from '@chakra-ui/react'
import api from '@seplis/api'
import { IPageCursorResult } from '@seplis/interfaces/page'
import { ISliderItem } from '@seplis/interfaces/slider'
import { useInfiniteQuery } from '@tanstack/react-query'
import { ReactNode, useEffect, useState } from 'react'
import { useFocusable, FocusContext, FocusHandler } from '@noriginmedia/norigin-spatial-navigation'
import { Poster } from './poster'
import './slider.less'

interface IProps<S = undefined> {
    title?: string,
    url: string,
    hideIfEmpty?: boolean,
    onFocus?: FocusHandler,
    onItemSelected?: (item: S) => void
    parseItem: (item: S) => ISliderItem
}

export default function Slider<S = undefined>({ title, url, hideIfEmpty = false, parseItem, onFocus, onItemSelected }: IProps<S>) {
    const [items, setItems] = useState<ISliderItem[]>([])
    const [index, setIndex] = useState(0)
    const [displayItemCount, setDisplayItemCount] = useState(() => (rowWidthItems()))
    const { ref, focusKey } = useFocusable({ onFocus })
    const loadPerPage = 12

    const { data, isInitialLoading, fetchNextPage } = useInfiniteQuery(['slider', title, url], async ({ pageParam = null }) => {
        const data = await api.get<IPageCursorResult<S>>(url, {
            params: {
                per_page: loadPerPage * 2,
                cursor: pageParam,
            }
        })
        return data.data
    }, {
        getNextPageParam: (lastPage) => { return lastPage.cursor ?? undefined },
    })

    useEffect(() => {
        const items = data?.pages.flatMap((page) => page.items.map((item) => {
            const i = parseItem(item)
            i.data = item
            return i
        })) ?? []
        setItems(items)
    }, [data])

    const onCardFocus = (layout: any, props: any, details: any) => {
        const event = details.event as KeyboardEvent
        if (event?.code == 'ArrowRight') {
            if (items.length - index >= displayItemCount) {
                if (layout.node.getAttribute('data-view-index') > 1)
                    setIndex(index + 1)
                if ((index % loadPerPage) === 0)
                    fetchNextPage()
            }
        } else if (!event || event?.code == 'ArrowLeft') {
            if (index > 0)
                setIndex(index - 1)
        }
    }

    function handleResize() {
        setDisplayItemCount(rowWidthItems())
    }
    useEffect(() => {
        window.addEventListener('resize', handleResize)
        return () => {
            return window.removeEventListener('resize', handleResize)
        }
    }, [])

    if (hideIfEmpty && !isInitialLoading && items.length === 0)
        return null

    return <FocusContext.Provider value={focusKey}>
        <Box ref={ref}>
            {title && <Heading className="row-header">{title}</Heading>}
            <HStack className="slider" alignItems="stretch">
                {(!isInitialLoading && items) ? <>
                    <Cards<S>
                        items={items.slice(index, index + displayItemCount)}
                        onFocus={onCardFocus}
                        onItemSelected={onItemSelected}
                    />
                    <PeekCard index={index} items={items} next={false} setIndex={setIndex} fetchNextPage={fetchNextPage} />
                    <PeekCard index={index} items={items} next={true} setIndex={setIndex} fetchNextPage={fetchNextPage} />
                </> : <SkeletonCards />}
            </HStack>
        </Box>
    </FocusContext.Provider>
}


export function Cards<S = any>({ items, onFocus, onItemSelected }: { items: ISliderItem[], onFocus: FocusHandler, onItemSelected: (item: S) => void }) {
    const { ref, focusKey } = useFocusable()
    return <FocusContext.Provider value={focusKey}>
        <HStack ref={ref} width="100%">
            {items.map((item, index) => <Card<S>
                key={item.key}
                item={item}
                onFocus={onFocus}
                onItemSelected={onItemSelected}
                viewItemIndex={index}
            />)}
            {[...Array(rowWidthItems() - items.length).keys()].map(i => <EmptyCard key={`empty-${i}`} />)}
        </HStack>
    </FocusContext.Provider>
}


export function Card<S = any>({ item, onFocus, onItemSelected, viewItemIndex }: { item: ISliderItem, onFocus: FocusHandler, onItemSelected: (item: S) => void, viewItemIndex?: number }) {
    const { ref, focused } = useFocusable({
        onFocus: onFocus,
        onEnterPress: () => {
            onItemSelected(item.data)
        },
    })
    return <Flex
        className={`slider-item ${focused ? 'focused' : ''}`}
        key={item.key} ref={ref}
        data-view-index={viewItemIndex}
        borderRadius="md"
        cursor="pointer"
        overflow="hidden"
        grow="1"
        direction="column"
        onClick={() => {
            onItemSelected(item.data)
        }}
    >
        {item.topText !== undefined && <TextBox>{item.topText}</TextBox>}
        <Box className="poster-container" borderRadius="0">
            <Poster url={`${item.img}@SX320.webp`} title={item.title} />
        </Box>
        {item.bottomText !== undefined && <TextBox>{item.bottomText}</TextBox>}
    </Flex>
}


function TextBox({ children }: { children: ReactNode }) {
    return <Box
        backgroundColor="black"
        textAlign="center"
        padding="0.25rem"
        fontSize={['0.7rem', '1rem']}
    >
        {children}
    </Box>
}


function EmptyCard() {
    return <Box className="poster-container slider-item"></Box>
}


export function SkeletonCards() {
    return <>
        {[...Array(rowWidthItems()).keys()].map((key) => (
            <Skeleton key={`skeleton-${key}`} className="poster-container slider-item" rounded="md" width="100%" height="100%" />
        ))}
    </>
}


interface IPeekCardProps {
    index: number
    items: ISliderItem[]
    setIndex: React.Dispatch<React.SetStateAction<number>>
    fetchNextPage: () => void
    next: boolean
}
function PeekCard({ index, items, next, setIndex, fetchNextPage }: IPeekCardProps) {
    const displayCount = rowWidthItems()
    let itemIndex = 0
    if (next) {
        itemIndex = index + displayCount
        if (items.length <= index + displayCount)
            return
    } else {
        itemIndex = index - 1
        if (index < 1)
            return
    }

    const prevClick = () => {
        setIndex((index) => {
            let i = index - displayCount
            if (i < 0)
                i = 0
            return i
        })
    }

    const nextClick = () => {
        setIndex((index) => {
            fetchNextPage()
            let i = index + displayCount
            if (i > (items.length - 1))
                i = (items.length - 1) - displayCount
            return i
        })
    }

    return <div className={`slider-peek ${next ? 'next' : 'prev'}`}>
        {(items[itemIndex]?.img) &&
            <div className="image">
                <Image
                    src={`${items[itemIndex].img}@SX320.webp`}
                />
            </div>}

        <div className="background"></div>
        <div className="button" onClick={next ? nextClick : prevClick}>
            {next ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </div>
    </div>
}


function rowWidthItems() {
    const width = window.innerWidth
    if (width >= 1600)
        return 12
    else if (width >= 1100)
        return 7
    else if (width >= 600)
        return 6
    else
        return 3
}