import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { useGetPlayServerMedia } from '../api/play-server-request-media.api'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import {
    PREFERRED_AUDIO_LANGS,
    PREFERRED_SUBTITLE_LANGS,
} from '../constants/play-language.constants'
import { usePlaySettings } from '../hooks/use-play-settings'
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
    const resumeTimeRef = useRef<number>(defaultStartTime ?? 0)
    const currentTimeRef = useRef<number>(defaultStartTime ?? 0)
    const lastSaveTimeRef = useRef<number>(defaultStartTime ?? 0)
    const finishedFiredRef = useRef(false)
    const [isVideoLoading, setIsVideoLoading] = useState(true)

    const playSettings = usePlaySettings('play-settings')
    const { settings } = playSettings

    const { data, isLoading, error, isRefetching } = useGetPlayServerMedia({
        playRequestSource: source,
        maxBitrate: maxBitrate < MAX_BITRATE ? maxBitrate : undefined,
        audio,
        forceTranscode,
        ...settings,
        options: {
            refetchOnWindowFocus: false,
            staleTime: Infinity,
        },
    })
    const handleTimeUpdate = useEffectEvent(
        (currentTime: number, duration: number) => {
            currentTimeRef.current = currentTime
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
        if (!forceTranscode) {
            setForceTranscode(true)
        }
    }

    useEffect(() => {
        resumeTimeRef.current = currentTimeRef.current
        setIsVideoLoading(true)
    }, [data])

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
            startTime={resumeTimeRef.current}
            onSourceChange={setSource}
            onBitrateChange={handleBitrateChange}
            onAudioChange={(audio) => {
                setAudioLang(audio)
                onAudioChange?.(audio)
            }}
            onPlayError={handlePlayError}
            onForceTranscodeChange={setForceTranscode}
            onVideoReady={() => setIsVideoLoading(false)}
            onVideoError={handlePlayError}
            onTimeUpdate={handleTimeUpdate}
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
            advancedSettings={settings}
            onAdvancedSettingsChange={playSettings.update}
            onAdvancedSettingsReset={playSettings.reset}
            isAdvancedDefault={playSettings.isDefault}
        />
    )
}
