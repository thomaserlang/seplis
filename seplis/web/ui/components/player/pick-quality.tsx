import { Box, Flex } from '@chakra-ui/react'
import { IPlaySource } from '@seplis/interfaces/play-server'

interface IProps {
    source: IPlaySource
    maxBitrate: number
    onChange: (width: number) => void
}

export const MAX_BITRATE = 200000000

export function PickQuality({ source, maxBitrate, onChange }: IProps) {
    return (
        <Flex gap="0.25rem" direction="column">
            <Box
                cursor="pointer"
                textStyle={maxBitrate === MAX_BITRATE ? 'selectedText' : null}
                onClick={() => {
                    onChange?.(MAX_BITRATE)
                }}
            >
                Max
            </Box>
            {maxBitrates.map((bitrate) => {
                if (source.bit_rate >= bitrate)
                    return (
                        <Box
                            key={bitrate}
                            cursor="pointer"
                            textStyle={
                                maxBitrate === bitrate ? 'selectedText' : null
                            }
                            onClick={() => {
                                onChange?.(bitrate)
                            }}
                        >
                            {bitratePretty(bitrate)}
                        </Box>
                    )
            })}
        </Flex>
    )
}

export function getDefaultMaxBitrate() {
    const maxBitrate = localStorage.getItem('maxBitrate')
    if (maxBitrate) return parseInt(maxBitrate)
    return MAX_BITRATE
}

const maxBitrates = [
    120000000, // 120 Mbps
    12000000, // 12 Mbps
    8000000, // 8 Mbps
    6000000, // 6 Mbps
    4000000, // 4 Mbps
    3000000, // 3 Mbps
    1500000, // 1.5 Mbps
    720000, // 720 kbps
    420000, // 420 kbps
]

export function getBitrate(source: IPlaySource) {
    const bitrate = getDefaultMaxBitrate()
    if (source.bit_rate <= bitrate) return source.bit_rate
    return bitrate
}

export function bitrateDisplay(maxBitrate: number, source: IPlaySource) {
    if (maxBitrate < source.bit_rate) {
        return bitratePretty(maxBitrate)
    } else {
        return 'Max'
    }
}

export function bitratePretty(bitrate: number) {
    let i = -1
    const byteUnits = [' kbps', ' Mbps']
    do {
        bitrate = bitrate / 1000
        i++
    } while (bitrate > 1000)

    const formattedBitrate = Math.max(bitrate, 0.1)
        .toFixed(1)
        .replace(/\.0$/, '')
    return formattedBitrate + byteUnits[i]
}
