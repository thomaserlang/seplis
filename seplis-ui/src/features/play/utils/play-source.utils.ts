import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
} from '../types/play-source.types'
import { getDefaultMaxBitrate } from './play-bitrate.utils'

export function playSourceStr(source: PlaySource) {
    let s = `${source.resolution} ${source.codec.toUpperCase()}`
    if (source.video_color_range == 'hdr')
        if (source.video_color_range_type == 'dovi') s += ' Dolby Vision'
        else s += ` HDR`
    return s
}

export function pickStartSource(
    playServers: PlayRequestSources[],
    defaultMaxBitrate?: number,
) {
    let s: PlayRequestSource = {
        request: playServers[0].request,
        source: playServers[0].sources[0],
    }
    const maxBitrate = defaultMaxBitrate || getDefaultMaxBitrate()
    for (const playServer of playServers.reverse())
        for (const source of playServer.sources)
            if (source.bit_rate <= maxBitrate)
                s = {
                    request: playServer.request,
                    source: source,
                }
    return s
}
