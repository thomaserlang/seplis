import { Box, Flex } from '@chakra-ui/react'
import { IPlaySource } from '@seplis/interfaces/play-server'


interface IProps {
    source: IPlaySource,
    selectedWidth?: number
    onChange: (width: number) => void
}

export function PickQuality({ source, selectedWidth, onChange }: IProps) {
    return <Flex
        gap="0.25rem"
        direction="column"
    >
        {Object.entries(resolutionNames).sort((a, b) => parseInt(b[0]) - parseInt(a[0])).map(([width, value]) => {
            const w = parseInt(width)
            if (source.width >= w)
                return <Box
                    key={width}
                    textStyle={(resolutionToText(w) == resolutionToText(selectedWidth)) || (!selectedWidth && (resolutionToText(w) == resolutionToText(source.width))) ? 'selectedText' : null}
                    cursor="pointer"
                    onClick={() => {
                        localStorage.setItem('resolutionWidth', w.toString())
                        if (onChange) onChange(w)
                    }}
                >
                    {value}
                </Box>
        })}
    </Flex>
}


export function getDefaultResolutionWidth() {
    const w = localStorage.getItem('resolutionWidth')
    // Fix for old error that would set the requested resolution to requestedResolution - 200
    if (w && parseInt(w) == 1720)
        return 1920
    if (w)
        return parseInt(w)
    return 1920
}


export function getResolutionWidth(source: IPlaySource) {
    const w = getDefaultResolutionWidth()
    return (w > source.width) ? source.width : w
}


const resolutionNames: { [key: string]: string } = {
    '7680': '8K',
    '3840': '4K',
    '2560': '1440p',
    '1920': '1080p',
    '1280': '720p',
    '854': '480p',
    '640': '360p',
    '256': '144p',
}


export function resolutionToText(width: number) {
    if (!width) return 'Auto'
    if (width <= 256)
        return '144p'
    else if (width <= 426)
        return '240p'
    else if (width <= 640)
        return '360p'
    else if (width <= 854)
        return '480p'
    else if (width <= 1280)
        return '720p'
    else if (width <= 1920)
        return '1080p'
    else if (width <= 2560)
        return '1440p'
    else if (width <= 4096)
        return '4K'
    else if (width <= 8192)
        return '8K'
    return `W: ${width}`
}

