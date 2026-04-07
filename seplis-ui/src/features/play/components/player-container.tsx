import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useGetPlayRequestSources } from '../api/play-request-sources.api'
import { PlayRequest } from '../types/play-source.types'
import { PlayerProps } from '../types/player.types'
import { Player } from './player-video'
import { PlayerView } from './player-view'

interface Props extends PlayerProps {
    playRequests: PlayRequest[]
}

export function PlayerContainer({ playRequests, ...props }: Props) {
    const { data, isLoading, error } = useGetPlayRequestSources({
        playRequests,
        options: {
            refetchOnWindowFocus: false,
            staleTime: Infinity,
        },
    })

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data || data.length === 0)
        return (
            <ErrorBox message="No play server available, please try again later." />
        )

    return (
        <Player.Provider>
            <PlayerView playRequestsSources={data} {...props} />
        </Player.Provider>
    )
}
