import { Box } from '@chakra-ui/react'
import { IPlayRequest, IPlayServerRequestSource, IPlayServerRequestSources, IPlaySource } from '@seplis/interfaces/play-server'
import { getDefaultResolutionWidth, widthToText } from './pick-quality'

interface IProps {
    playServers: IPlayServerRequestSources[],
    selected: IPlayServerRequestSource,
    onChange: (requestSource: IPlayServerRequestSource) => void,
}

export function PickSource({ playServers, selected, onChange }: IProps) {
    return <Box>
        {playServers.map(server => (
            server.sources.sort((a, b) => b.width - a.width).map(source => (
                <Box
                    key={`${server.request.play_id}-${source.index}`}
                    textStyle={isSelected(selected, server.request, source) ? 'selectedText' : null}
                    cursor="pointer"
                    onClick={() => {
                        const r: IPlayServerRequestSource = {
                            request: server.request,
                            source: source,
                        }
                        localStorage.setItem('resolutionWidth', source.width.toString())
                        if (onChange) onChange(r)
                    }}
                >
                    {`${widthToText(source.width)} ${source.codec}`}
                </Box>
            ))
        ))}
    </Box>
}


function isSelected(selected: IPlayServerRequestSource, request: IPlayRequest, source: IPlaySource) {
    return ((selected.request.play_id == request.play_id) &&
        (source.index == selected.source.index))
}


export function pickStartSource(playServers: IPlayServerRequestSources[]) {
    let s: IPlayServerRequestSource = {
        request: playServers[0].request,
        source: playServers[0].sources[0],
    }
    const w = getDefaultResolutionWidth() || 1920
    for (const playServer of playServers.reverse())
        for (const source of playServer.sources)
            if (source.width <= w)
                s = {
                    request: playServer.request,
                    source: source,
                }
    return s
}