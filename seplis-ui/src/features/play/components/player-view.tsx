import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { useEffectEvent, useRef, useState } from 'react'
import {
    PREFERRED_AUDIO_LANGS,
    PREFERRED_SUBTITLE_LANGS,
} from '../constants/play-language.constants'
import { usePlaySettings } from '../hooks/use-play-settings'
import { PlayerProps } from '../types/player.types'
import {
    pickStartAudio,
    pickStartSource,
    pickStartSubtitle,
} from '../utils/play-source.utils'
import { Player, PlayerVideo } from './player-video'

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
    const playSettings = usePlaySettings('play-settings')
    const [source, setSource] = useState<PlayRequestSource>(() =>
        pickStartSource(playRequestsSources, playSettings.settings.maxBitrate),
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

    const handleTimeUpdate = useEffectEvent(
        (currentTime: number, duration: number) => {
            currentTimeRef.current = currentTime
            if (finishedFiredRef.current) return
            if (currentTime >= duration * 0.9) {
                finishedFiredRef.current = true
                onFinished?.()
            } else if (Math.abs(currentTime - lastSaveTimeRef.current) >= 10) {
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

    return (
        <Player.Provider>
            <PlayerVideo
                playRequestSource={source}
                playRequestsSources={playRequestsSources}
                title={title}
                secondaryTitle={secondaryTitle}
                onClose={onClose}
                audio={audio}
                forceTranscode={forceTranscode}
                defaultStartTime={defaultStartTime}
                onSourceChange={setSource}
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
        </Player.Provider>
    )
}
