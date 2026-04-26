import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySourceStream,
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
    toLangKey,
} from '../utils/play-source.utils'
import { Player, PlayerVideo, type PlayErrorEvent } from './player-video'

interface Props extends PlayerProps {
    playRequestsSources: PlayRequestSources[]
}

export function PlayerView({
    playRequestsSources,
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    onSavePosition,
    onFinished,
    defaultAudioKey,
    defaultSubtitleKey,
    defaultStartTime,
    onAudioChange,
    onSubtitleChange,
}: Props) {
    const playSettings = usePlaySettings('play-settings')
    const [source, setSource] = useState<PlayRequestSource>(() =>
        pickStartSource(playRequestsSources, playSettings.settings.maxBitrate),
    )
    const [audio, setAudio] = useState<PlaySourceStream | undefined>(
        pickStartAudio({
            playSource: source.source,
            defaultAudioKey:
                defaultAudioKey ?? playSettings.settings.defaultAudioKey,
            preferredAudioLangs: PREFERRED_AUDIO_LANGS,
        }),
    )
    const [defaultSubtitle] = useState<PlaySourceStream | undefined>(
        pickStartSubtitle({
            playSource: source.source,
            defaultSubtitleKey:
                defaultSubtitleKey ?? playSettings.settings.defaultSubtitleKey,
            preferredSubtitleLangs: PREFERRED_SUBTITLE_LANGS,
            audio,
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

    const handlePlayError = useEffectEvent((event: PlayErrorEvent) => {
        if (forceTranscode) return
        if (event.type !== 'stall_timeout') return
        setForceTranscode(true)
    })

    const handleVideoError = useEffectEvent(() => {
        if (!forceTranscode) {
            setForceTranscode(true)
        }
    })

    return (
        <Player.Provider>
            <PlayerVideo
                playRequestSource={source}
                playRequestsSources={playRequestsSources}
                title={title}
                secondaryTitle={secondaryTitle}
                onClose={onClose}
                onPlayNext={onPlayNext}
                audio={audio}
                forceTranscode={forceTranscode}
                defaultStartTime={defaultStartTime}
                onSourceChange={setSource}
                onAudioChange={(audio) => {
                    setAudio(audio)
                    playSettings.update({
                        defaultAudioKey: toLangKey(audio),
                    })
                    onAudioChange?.(audio)
                }}
                onPlayError={handlePlayError}
                onForceTranscodeChange={setForceTranscode}
                onVideoError={handleVideoError}
                onTimeUpdate={handleTimeUpdate}
                defaultSubtitle={defaultSubtitle}
                onSubtitleChange={(subtitle) => {
                    onSubtitleChange?.(subtitle)
                    playSettings.update({
                        defaultSubtitleKey: toLangKey(subtitle),
                    })
                }}
                preferredAudioLangs={PREFERRED_AUDIO_LANGS}
                preferredSubtitleLangs={PREFERRED_SUBTITLE_LANGS}
                playSettings={playSettings}
            />
        </Player.Provider>
    )
}
