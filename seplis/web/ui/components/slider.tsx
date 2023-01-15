import { ChevronLeftIcon, ChevronRightIcon } from "@chakra-ui/icons"
import { Box, Center, HStack, Image, Skeleton, Text } from "@chakra-ui/react"
import api from "@seplis/api"
import { IPageResult } from "@seplis/interfaces/page"
import { ISliderItem } from "@seplis/interfaces/slider"
import { useQuery } from "@tanstack/react-query"
import { useCallback, useEffect, useState } from "react"
import { useFocusable, FocusContext, FocusHandler } from "@noriginmedia/norigin-spatial-navigation"

import './slider.less'

interface IProps<S = undefined> {
    title: string,
    url: string,
    onFocus?: FocusHandler,
    parseItem: (items: S) => ISliderItem
}

export default function Slider<S = undefined>({ title, url, parseItem, onFocus }: IProps<S>) {
    const [items, setItems] = useState<ISliderItem[]>([])
    const [page, setPage] = useState(1)
    const [index, setIndex] = useState(0)
    const [displayItemCount, setDisplayItemCount] = useState(() => (rowWidthItems()))
    const { ref, focusKey } = useFocusable({ onFocus })
    const loadPerPage = 12

    const { isInitialLoading } = useQuery([title], async () => {
        const data = await api.get<IPageResult<S>>(url, {
            params: {
                per_page: loadPerPage*2,
            }
        })
        const newItems: ISliderItem[] = []
        for (const item of data.data.items)
            newItems.push(parseItem(item))
        setPage(1)
        setIndex(0)
        setItems(newItems)
        return data
    }, {
        keepPreviousData: true
    })

    useEffect(() => {
        if (page == 1)
            return
        const fetch = async () => {
            const data = await api.get<IPageResult<S>>(url, {
                params: {
                    per_page: loadPerPage,
                    page: page + 1,
                }
            })
            const newItems: ISliderItem[] = []
            for (const item of data.data.items)
                newItems.push(parseItem(item))
            setItems([...items, ...newItems])
        }
        fetch()
    }, [page])

    const onCardFocus = (layout: any, props: any, details: any) => {
        const event = details.event as KeyboardEvent
        if (event?.code == 'ArrowRight') {
            if (items.length-index >= displayItemCount) {
                if (layout.node.getAttribute('data-view-index') > 1)
                    setIndex(index+1)
                if ((index % loadPerPage) === 0)
                    setPage(page+1)
            }
        } else if (!event || event?.code == 'ArrowLeft') {
            if (index>0)
                setIndex(index-1)
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

    return <FocusContext.Provider value={focusKey}>
        <Box ref={ref}>
            <h2 className="row-header">{title}</h2>
            <HStack className="slider">
                {(!isInitialLoading && items) ? <>
                    <Cards items={items.slice(index, index + displayItemCount)} onFocus={onCardFocus} />
                    <PeekCard index={index} items={items} next={false} setIndex={setIndex} setPage={setPage} />
                    <PeekCard index={index} items={items} next={true} setIndex={setIndex} setPage={setPage} />
                </> : SkeletonCards()}
            </HStack>
        </Box>
    </FocusContext.Provider>
}


function Cards({ items, onFocus }: { items: ISliderItem[], onFocus: FocusHandler }) {
    const { ref, focusKey } = useFocusable({
    })
    return <FocusContext.Provider value={focusKey}>
        <HStack ref={ref} width="100%">
            {items.map((item, index) => <Card key={item.key} item={item} onFocus={onFocus} viewItemIndex={index} />)}
            {[...Array(rowWidthItems() - items.length).keys()].map(i => <EmptyCard key={`empty-${i}`} />)}
        </HStack>
    </FocusContext.Provider>
}


function Card({ item, onFocus, viewItemIndex }: { item: ISliderItem, onFocus: FocusHandler, viewItemIndex: number }) {
    const { ref, focused } = useFocusable({
        onFocus: onFocus,    
    })
    return <Box className={`slider-item ${focused?'focused':''}`} key={item.key} ref={ref} data-view-index={viewItemIndex} >
        <Image
            src={`${item.img}@SX320.webp`}
            fallback={<Center height='100%'><Text>
                {item.title || 'No title'}
            </Text></Center>}
        />
    </Box>
}


function EmptyCard() {
    return <Box className="slider-item"></Box>
}


function SkeletonCards() {
    return [...Array(rowWidthItems()).keys()].map((key) => (
        <Skeleton key={`skeleton-${key}`} className="slider-item" />
    ))
}


interface IPeekCardProps {
    index: number
    items: ISliderItem[]
    setIndex: React.Dispatch<React.SetStateAction<number>>
    setPage: React.Dispatch<React.SetStateAction<number>>
    next: boolean
}
function PeekCard({ index, items, next, setIndex, setPage }: IPeekCardProps) {
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
            setPage((page) => page + 1)
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