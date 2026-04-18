import { PlaySource } from '../types/play-source.types'

export function playSourceBitrateStr(bitrate: number, source: PlaySource) {
    if (bitrate < source.bitrate) return bitratePretty(bitrate)
    return `${bitratePretty(source.bitrate)} (source)`
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
