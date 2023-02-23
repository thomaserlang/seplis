import { Box } from '@chakra-ui/react'
import { IPlayRequest, IPlayServerRequestSource, IPlayServerRequestSources, IPlaySource } from '@seplis/interfaces/play-server'
import { widthToText } from './pick-quality'

interface IProps {
    playServers: IPlayServerRequestSources[],
    selected: IPlayServerRequestSource,
    onChange: (requestSource: IPlayServerRequestSource) => void,
}

export function PickSource({ playServers, selected, onChange }: IProps) {
    let topWidth = 0
    const sourceWidths: number[] = []

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
    for (const playServer of playServers.reverse())
        for (const source of playServer.sources)
            if (source.width <= 1920)
                s = {
                    request: playServer.request,
                    source: source,
                }
    return s
}
