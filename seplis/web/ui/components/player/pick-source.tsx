import { Box, Flex } from '@chakra-ui/react'
import {
    IPlayRequest,
    IPlayServerRequestSource,
    IPlayServerRequestSources,
    IPlaySource,
} from '@seplis/interfaces/play-server'
import { getDefaultMaxBitrate } from './pick-quality'

interface IProps {
    playServers: IPlayServerRequestSources[]
    selected: IPlayServerRequestSource
    onChange: (requestSource: IPlayServerRequestSource) => void
}

export function PickSource({ playServers, selected, onChange }: IProps) {
    return (
        <Flex gap="0.25rem" direction="column">
            {playServers.map((server) =>
                server.sources
                    .sort((a, b) => b.width - a.width)
                    .map((source) => (
                        <Box
                            key={`${server.request.play_id}-${source.index}`}
                            textStyle={
                                isSelected(selected, server.request, source)
                                    ? 'selectedText'
                                    : null
                            }
                            cursor="pointer"
                            onClick={() => {
                                const r: IPlayServerRequestSource = {
                                    request: server.request,
                                    source: source,
                                }
                                if (onChange) onChange(r)
                            }}
                        >
                            {renderPlaySource(source)}
                        </Box>
                    ))
            )}
        </Flex>
    )
}

export function renderPlaySource(source: IPlaySource) {
    let s = `${source.resolution} ${source.codec.toUpperCase()}`
    if (source.video_color_range == 'hdr')
        if (source.video_color_range_type == 'dovi') s += ' Dolby Vision'
        else s += ` HDR`
    return s
}

function isSelected(
    selected: IPlayServerRequestSource,
    request: IPlayRequest,
    source: IPlaySource
) {
    return (
        selected.request.play_id == request.play_id &&
        source.index == selected.source.index
    )
}

export function pickStartSource(
    playServers: IPlayServerRequestSources[],
    defaultMaxBitrate?: number
) {
    let s: IPlayServerRequestSource = {
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
