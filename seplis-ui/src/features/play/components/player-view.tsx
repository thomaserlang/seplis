import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useMedia } from '@videojs/react'
import { useEffect, useState } from 'react'
import { useGetPlayServerMedia } from '../api/play-server-media.api'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import { getDefaultMaxBitrate } from '../utils/play-bitrate.utils'
import { pickStartSource } from '../utils/play-source.utils'
import { PlayerVideo } from './player-video'

interface Props {
    playRequestsSources: PlayRequestSources[]
    title?: string
    subtitle?: string
    onClose?: () => void
}

export function PlayerView({
    playRequestsSources,
    title,
    subtitle,
    onClose,
}: Props) {
    const [source, setSource] = useState<PlayRequestSource>(() =>
        pickStartSource(playRequestsSources),
    )
    const [maxBitrate, setMaxBitrate] = useState<number>(() =>
        getDefaultMaxBitrate(),
    )
    const [audioLang, setAudioLang] = useState<string | undefined>(undefined)
    const [forceTranscode, setForceTranscode] = useState(false)

    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
        maxBitrate: maxBitrate < MAX_BITRATE ? maxBitrate : undefined,
        audio: audioLang,
        forceTranscode,
    })
    const media = useMedia()

    useEffect(() => {
        if (!media) return
        media.onloadeddata = () => {
            media.play()
        }
        const savedVolume = localStorage.getItem('player-volume')
        media.volume = savedVolume !== null ? parseFloat(savedVolume) : 0.5
        media.onvolumechange = () => {
            localStorage.setItem('player-volume', String(Math.round(media.volume * 100) / 100))
        }
    }, [media])

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data) return <ErrorBox message="No playable source found" />

    const handleBitrateChange = (bitrate: number) => {
        localStorage.setItem('maxBitrate', String(bitrate))
        setMaxBitrate(bitrate)
    }

    return (
        <PlayerVideo
            media={data}
            currentPlayRequestSource={source}
            playRequestsSources={playRequestsSources}
            title={title}
            subtitle={subtitle}
            onClose={onClose}
            maxBitrate={maxBitrate}
            audioLang={audioLang}
            forceTranscode={forceTranscode}
            onSourceChange={setSource}
            onBitrateChange={handleBitrateChange}
            onAudioLangChange={setAudioLang}
            onForceTranscodeChange={setForceTranscode}
        />
    )
}
