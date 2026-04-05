import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import { PlaySource } from '../types/play-source.types'

export function getDefaultMaxBitrate() {
    const maxBitrate = localStorage.getItem('maxBitrate')
    if (maxBitrate) return parseInt(maxBitrate)
    return MAX_BITRATE
}

export function getBitrate(source: PlaySource) {
    const bitrate = getDefaultMaxBitrate()
    if (source.bit_rate <= bitrate) return source.bit_rate
    return bitrate
}

export function playSourceBitrateStr(bitrate: number, source: PlaySource) {
    if (bitrate < source.bit_rate) return bitratePretty(bitrate)
    return `${bitratePretty(source.bit_rate)} (source)`
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
