import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useGetPlayRequestSources } from '../api/play-request-sources.api'
import { PlayRequest } from '../types/play-source.types'
import { PlayerView } from './player-view'

interface Props {
    playRequests: PlayRequest[]
    title?: string
    subtitle?: string
    onClose?: () => void
}

export function PlayerContainer({
    playRequests,
    title,
    subtitle,
    onClose,
}: Props) {
    const { data, isLoading, error } = useGetPlayRequestSources({
        playRequests,
    })

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data || data.length === 0)
        return (
            <ErrorBox message="No play server available, please try again later." />
        )

    return (
        <PlayerView
            playRequestsSources={data}
            title={title}
            subtitle={subtitle}
            onClose={onClose}
        />
    )
}
