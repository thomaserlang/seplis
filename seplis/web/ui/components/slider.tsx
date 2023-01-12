import { ChevronLeftIcon, ChevronRightIcon } from "@chakra-ui/icons";
import { Box, Center, Heading, HStack, Image, Skeleton, Text } from "@chakra-ui/react";
import api from "@seplis/api";
import { IPageResult } from "@seplis/interfaces/page";
import { ISliderItem } from "@seplis/interfaces/slider";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import './slider.less'

interface IProps<S = undefined> {
    title: string,
    url: string,
    parseItem: (items: S) => ISliderItem
}


export default function Slider<S = undefined>({title, url, parseItem}: IProps<S>) {
    const [items, setItems] = useState<ISliderItem[]>([])
    const [page, setPage] = useState(1)
    const [index, setIndex] = useState(0)

    const { isInitialLoading } = 
        useQuery([title], async () => {
            const data = await api.get<IPageResult<S>>(url, {
                params: {
                    per_page: 24,
                }
            })
            const newItems: ISliderItem[] = []
            for (const item of data.data.items)
                newItems.push(parseItem(item))
            setPage(1)
            setIndex(0)
            setItems(newItems)
        })
    
    useEffect(() => {
        if (page == 1)
            return
        const fetch = async () => {
            const data = await api.get<IPageResult<S>>(url, {
                params: {
                    per_page: 12,
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
    
    return RenderSlider(title, items, isInitialLoading, setPage, index, setIndex)    
}

function RenderSlider(
    title: string, 
    items: ISliderItem[], 
    isLoading: boolean, 
    setPage: React.Dispatch<React.SetStateAction<number>>,
    index: number,
    setIndex: React.Dispatch<React.SetStateAction<number>>
) {
    const [displayItemCount, setDisplayItemCount] = useState(() => (rowWidthItems()))

    function handleResize() {
        setDisplayItemCount(rowWidthItems())
    }
    useEffect(() => {
        window.addEventListener('resize', handleResize)
        return () => {
            return window.removeEventListener('resize', handleResize)
        }
    }, [])

    if (isLoading || !items) {
        return <Box> 
            <Heading as="h2" className="row-header">{title}</Heading>
            <Box className="slider">
                <HStack>
                    {[...Array(displayItemCount).keys()].map((key) => (                
                        <Skeleton key={`skeleton-${key}`} className="slider-item" />
                    ))}
                </HStack>
            </Box>
        </Box>
    }

    return <Box> 
        <Heading as="h2" className="row-header">{title}</Heading>
        <Box className="slider">
            <HStack>
                {items.slice(index, index+displayItemCount).map(item => (
                    <Box className="slider-item" key={item.key}>
                        <Image 
                            src={`${item.img}@SX320.webp`} 
                            fallback={<Center height='100%'><Text style={{fontSize: '1.4vw'}}>
                                {item.title || 'No title'}
                            </Text></Center>}
                        />
                    </Box>
                ))}


                {(items.length < displayItemCount) && [...Array(displayItemCount-items.length).keys()].map(key => (
                    <Box className="slider-item" key={`empty-${key}`}></Box>
                )) }
                {index > 0 && 
                    <div className="slider-button left-button" onClick={() => {
                        setIndex((index) => {
                            let i = index - displayItemCount
                            if (i < 0)
                                i = 0
                            return i
                        })
                    }}>
                        <ChevronLeftIcon boxSize="2vw" />
                    </div>}


                {items.length > index+displayItemCount && 
                    <div className="slider-button right-button" onClick={() => {
                        setIndex((index) =>  {
                            setPage((page) => page + 1)
                            let i = index + displayItemCount
                            if (i > (items.length - 1))
                                i = (items.length - 1) - displayItemCount
                            return i
                        })
                    }}>
                        <ChevronRightIcon boxSize="2vw" />
                    </div>}


            </HStack>
        </Box>
    </Box>
}

function rowWidthItems() {
    const width = window.innerWidth
    if (width >= 1600)
        return 12
    else if (width >= 1100)
        return 8
    else if (width >= 600)
        return 6
    else 
        return 4
}