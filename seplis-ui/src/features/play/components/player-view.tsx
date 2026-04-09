import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useMedia } from '@videojs/react'
import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { useGetPlayServerMedia } from '../api/play-server-media.api'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import {
    PREFERRED_AUDIO_LANGS,
    PREFERRED_SUBTITLE_LANGS,
} from '../constants/play-language.constants'
import { PlayerProps } from '../types/player.types'
import { getDefaultMaxBitrate } from '../utils/play-bitrate.utils'
import {
    pickStartAudio,
    pickStartSource,
    pickStartSubtitle,
} from '../utils/play-source.utils'
import { PlayerVideo } from './player-video'

interface Props extends PlayerProps {
    playRequestsSources: PlayRequestSources[]
}

export function PlayerView({
    playRequestsSources,
    title,
    secondaryTitle,
    onClose,
    onSavePosition,
    onFinished,
    defaultAudio,
    defaultSubtitle,
    defaultStartTime,
    onAudioChange,
    onSubtitleChange,
}: Props) {
    const [source, setSource] = useState<PlayRequestSource>(() =>
        pickStartSource(playRequestsSources),
    )
    const [maxBitrate, setMaxBitrate] = useState<number>(() =>
        getDefaultMaxBitrate(),
    )
    const [audio, setAudioLang] = useState<string | undefined>(
        pickStartAudio({
            playSource: source.source,
            defaultAudio,
            preferredAudioLangs: PREFERRED_AUDIO_LANGS,
        }),
    )
    const [forceTranscode, setForceTranscode] = useState(false)
    const forceTranscodeRef = useRef(forceTranscode)
    forceTranscodeRef.current = forceTranscode
    const resumeTimeRef = useRef<number>(defaultStartTime ?? 0)
    const lastSaveTimeRef = useRef<number>(defaultStartTime ?? 0)
    const finishedFiredRef = useRef(false)
    const [isVideoLoading, setIsVideoLoading] = useState(true)
    const { data, isLoading, error, isRefetching } = useGetPlayServerMedia({
        playRequestSource: source,
        maxBitrate: maxBitrate < MAX_BITRATE ? maxBitrate : undefined,
        audio,
        forceTranscode,
        options: {
            refetchOnWindowFocus: false,
            staleTime: Infinity,
        },
    })
    const media = useMedia()

    const handleTimeUpdate = useEffectEvent(
        (currentTime: number, duration: number) => {
            resumeTimeRef.current = currentTime
            if (finishedFiredRef.current) return
            if (currentTime >= duration * 0.9) {
                finishedFiredRef.current = true
                onFinished?.()
            } else if (currentTime - lastSaveTimeRef.current >= 10) {
                lastSaveTimeRef.current = currentTime
                onSavePosition?.(Math.round(currentTime))
            }
        },
    )

    const handlePlayError = () => {
        if (!forceTranscodeRef.current) {
            setIsVideoLoading(true)
            setForceTranscode(true)
        }
    }

    useEffect(() => {
        if (!media) return
        media.onloadedmetadata = () => {
            media.currentTime = resumeTimeRef.current
        }
        media.oncanplay = () => {
            setIsVideoLoading(false)
        }
        media.onerror = () => {
            handlePlayError()
        }
        media.ontimeupdate = () => {
            if (!media.duration) return
            handleTimeUpdate(media.currentTime, media.duration)
        }
        const savedVolume = localStorage.getItem('player-volume')
        media.volume = savedVolume !== null ? parseFloat(savedVolume) : 0.5
        media.onvolumechange = () => {
            localStorage.setItem(
                'player-volume',
                String(Math.round(media.volume * 100) / 100),
            )
        }
    }, [media])

    if (isLoading) return <PageLoader />
    if (error) return <ErrorBox errorObj={error} />
    if (!data) return <ErrorBox message="No playable source found" />

    const handleBitrateChange = (bitrate: number) => {
        if (bitrate >= source.source.bit_rate) {
            localStorage.removeItem('maxBitrate')
            setMaxBitrate(MAX_BITRATE)
        } else {
            localStorage.setItem('maxBitrate', String(bitrate))
            setMaxBitrate(bitrate)
        }
    }

    return (
        <PlayerVideo
            playServerMedia={data}
            playRequestSource={source}
            playRequestsSources={playRequestsSources}
            title={title}
            secondaryTitle={secondaryTitle}
            onClose={onClose}
            maxBitrate={maxBitrate}
            audio={audio}
            forceTranscode={forceTranscode}
            isVideoLoading={isVideoLoading || isRefetching}
            onSourceChange={setSource}
            onBitrateChange={handleBitrateChange}
            onAudioChange={(audio) => {
                setAudioLang(audio)
                onAudioChange?.(audio)
            }}
            onPlayError={handlePlayError}
            onForceTranscodeChange={setForceTranscode}
            defaultSubtitle={pickStartSubtitle({
                playSource: source.source,
                defaultSubtitle,
                preferredSubtitleLangs: PREFERRED_SUBTITLE_LANGS,
                audio,
            })}
            onSubtitleChange={(s) => {
                onSubtitleChange?.(s)
            }}
            preferredAudioLangs={PREFERRED_AUDIO_LANGS}
            preferredSubtitleLangs={PREFERRED_SUBTITLE_LANGS}
        />
    )
}
