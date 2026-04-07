import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useMedia } from '@videojs/react'
import { type CSSProperties, useEffect, useRef, useState } from 'react'
import { useGetPlayServerMedia } from '../api/play-server-media.api'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import { getDefaultMaxBitrate } from '../utils/play-bitrate.utils'
import { pickStartSource } from '../utils/play-source.utils'
import { PlayerVideo } from './player-video'

interface Props {
    playRequestsSources: PlayRequestSources[]
    title?: string
    secondaryTitle?: string
    onClose?: () => void
}

export function PlayerView({
    playRequestsSources,
    title,
    secondaryTitle,
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
    const forceTranscodeRef = useRef(forceTranscode)
    forceTranscodeRef.current = forceTranscode
    const resumeTimeRef = useRef<number | undefined>(undefined)
    const [frozenTimeStyle, setFrozenTimeStyle] = useState<CSSProperties | undefined>(undefined)
    const [isVideoLoading, setIsVideoLoading] = useState(true)
    const [suppressErrorDialog, setSuppressErrorDialog] = useState(false)

    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
        maxBitrate: maxBitrate < MAX_BITRATE ? maxBitrate : undefined,
        audio: audioLang,
        forceTranscode,
    })
    const media = useMedia()

    useEffect(() => {
        if (!media) return
        media.onloadedmetadata = () => {
            if (resumeTimeRef.current !== undefined) {
                media.currentTime = resumeTimeRef.current
                resumeTimeRef.current = undefined
            }
        }
        media.onloadeddata = () => {
            media.play()
        }
        media.oncanplay = () => {
            setIsVideoLoading(false)
            setSuppressErrorDialog(false)
        }
        media.onerror = () => {
            if (!forceTranscodeRef.current) {
                setSuppressErrorDialog(true)
                setIsVideoLoading(true)
                setForceTranscode(true)
            } else {
                setIsVideoLoading(false)
            }
        }
        media.onseeked = () => {
            setFrozenTimeStyle(undefined)
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

    const capturePosition = () => {
        if (!media) return
        resumeTimeRef.current = media.currentTime
        const fill = media.duration > 0 ? (media.currentTime / media.duration) * 100 : 0
        setFrozenTimeStyle({ '--media-slider-fill': `${fill}%` } as CSSProperties)
        setIsVideoLoading(true)
    }

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
            secondaryTitle={secondaryTitle}
            onClose={onClose}
            maxBitrate={maxBitrate}
            audioLang={audioLang}
            forceTranscode={forceTranscode}
            timeSliderStyle={frozenTimeStyle}
            isVideoLoading={isVideoLoading}
            suppressErrorDialog={suppressErrorDialog}
            onSourceChange={(s) => { capturePosition(); setSource(s) }}
            onBitrateChange={handleBitrateChange}
            onAudioLangChange={(lang) => { capturePosition(); setAudioLang(lang) }}
            onForceTranscodeChange={(v) => { capturePosition(); setForceTranscode(v) }}
        />
    )
}
