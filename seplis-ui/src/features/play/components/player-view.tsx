import { PlayRequestSources } from '../types/play-source.types'

import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import '@videojs/react/video/skin.css'
import { useState } from 'react'
import { useGetPlayServerMedia } from '../api/play-server-media.api'
import { pickStartSource } from '../utils/play-source.utils'
import { PlayerVideo } from './player-video'

interface Props {
    playRequestsSources: PlayRequestSources[]
    title?: string
    subtitle?: string
    loading?: boolean
    error?: Error | null
    onClose?: () => void
}

export function PlayerView({
    playRequestsSources,
    title,
    subtitle,
    onClose,
}: Props) {
    const [source] = useState(() => pickStartSource(playRequestsSources))
    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
    })

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data) return <ErrorBox message="No playable source found" />

    return (
        <PlayerVideo
            media={data}
            title={title}
            subtitle={subtitle}
            onClose={onClose}
        />
    )
}
