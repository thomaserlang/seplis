import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import {
    ChromecastProvider,
    useChromecast,
} from '@/features/play/components/chromecast/providers/chromecast-provider'
import { useRef } from 'react'
import { useGetPlayRequestSources } from '../api/play-request-sources.api'
import { PlayRequest, PlayRequestSources } from '../types/play-source.types'
import { PlayerProps } from '../types/player.types'
import { PlayerCastView } from './chromecast/components/player-cast-view'
import { Player } from './player-video'
import { PlayerView } from './player-view'

const CHROMECAST_APP_ID = import.meta.env.DEV ? '0BB2BE80' : 'EA4A67C4'

interface Props extends PlayerProps {
    playRequests: PlayRequest[]
}

export function PlayerContainer({ playRequests, ...props }: Props) {
    const { data, isLoading, error } = useGetPlayRequestSources({
        playRequests,
        options: {
            refetchOnWindowFocus: false,
        },
    })

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data || data.length === 0)
        return (
            <ErrorBox message="No play server available, please try again later." />
        )

    return (
        <ChromecastProvider receiverApplicationId={CHROMECAST_APP_ID}>
            <Player.Provider>
                <PlayerSwitch playRequestsSources={data} {...props} />
            </Player.Provider>
        </ChromecastProvider>
    )
}

interface SwitchProps extends PlayerProps {
    playRequestsSources: PlayRequestSources[]
}

function PlayerSwitch({ playRequestsSources, ...props }: SwitchProps) {
    const wasConnectedRef = useRef(false)
    const { isConnected } = useChromecast()

    if (isConnected) {
        wasConnectedRef.current = true
        return (
            <PlayerCastView
                playRequestsSources={playRequestsSources}
                {...props}
            />
        )
    }

    return <PlayerView playRequestsSources={playRequestsSources} {...props} />
}
