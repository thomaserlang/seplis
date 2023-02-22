import { Box } from '@chakra-ui/react'
import { IPlaySource } from '@seplis/interfaces/play-server'


interface IProps {
    source: IPlaySource,
    selectedWidth?: number
}

export function PickQuality({ source, selectedWidth }: IProps) {
    return <Box>
        {Object.entries(resolutionNames).sort((a, b) => parseInt(b[0]) - parseInt(a[0])).map(([width, value]) => {
            const w = parseInt(width)
            if (source.width >= w)
                return <Box 
                    key={width}
                    textStyle={(w == selectedWidth) || (w == source.width) ? 'selectedText' : null}
                >
                    {value}
                </Box>
        })}
    </Box>
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


export function widthToText(width: number) {
    if (width in resolutionNames)
        return resolutionNames[width]
    return `W: ${width}`
}

