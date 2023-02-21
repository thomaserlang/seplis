import { IPlayServerRequestSource, IPlayServerRequestSources } from '@seplis/interfaces/play-server'

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