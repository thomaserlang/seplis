import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { useEffectEvent, useRef, useState } from 'react'
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
    const currentTimeRef = useRef<number>(defaultStartTime ?? 0)
    const lastSaveTimeRef = useRef<number>(defaultStartTime ?? 0)
    const finishedFiredRef = useRef(false)

    const playSettings = usePlaySettings('play-settings')

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
            playRequestSource={source}
            playRequestsSources={playRequestsSources}
            title={title}
            secondaryTitle={secondaryTitle}
            onClose={onClose}
            maxBitrate={maxBitrate}
            audio={audio}
            forceTranscode={forceTranscode}
            defaultStartTime={defaultStartTime}
            onSourceChange={setSource}
            onBitrateChange={handleBitrateChange}
            onAudioChange={(audio) => {
                setAudioLang(audio)
                onAudioChange?.(audio)
            }}
            onPlayError={handlePlayError}
            onForceTranscodeChange={setForceTranscode}
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
            playSettings={playSettings}
        />
    )
}
