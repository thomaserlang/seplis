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
                    textStyle={(w == selectedWidth) || (!selectedWidth && (w == source.width)) ? 'selectedText' : null}
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
    '852': '480p',
    '480': '360p',
    '352': '144p',
}


export function resolutionToText(width: number) {
    if (!width) return 'Auto'
    if (width in resolutionNames)
        return resolutionNames[width]
    return `W: ${width}`
}

