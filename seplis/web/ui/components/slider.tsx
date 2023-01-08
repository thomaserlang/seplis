import { ChevronLeftIcon, ChevronRightIcon } from "@chakra-ui/icons";
import { Box, Center, Heading, HStack, Image, Skeleton, Text } from "@chakra-ui/react";
import { ISliderItem } from "@seplis/interfaces/slider";
import { useEffect, useState } from "react";

import './slider.less'

interface IProps {
    title: string,
    items: ISliderItem[], 
    isLoading: boolean,
}


export default function Slider({title, items, isLoading = false}: IProps) {
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
                {items.slice(0, displayItemCount).map(item => (
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
                <div className="slider-button left-button"><Center height="100%"><ChevronLeftIcon boxSize="2vw" /></Center></div>
                <div className="slider-button right-button"><Center height="100%"><ChevronRightIcon boxSize="2vw" /></Center></div>
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