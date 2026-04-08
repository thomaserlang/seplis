import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useMedia } from '@videojs/react'
import {
    type CSSProperties,
    useEffect,
    useEffectEvent,
    useRef,
    useState,
} from 'react'
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
    const resumeTimeRef = useRef<number | undefined>(defaultStartTime)
    const lastSaveTimeRef = useRef<number>(defaultStartTime ?? 0)
    const finishedFiredRef = useRef(false)
    const [activeSubtitle, setActiveSubtitle] = useState<string | undefined>(
        () =>
            pickStartSubtitle({
                playSource: source.source,
                defaultSubtitle,
                preferredSubtitleLangs: PREFERRED_SUBTITLE_LANGS,
                audio: pickStartAudio({
                    playSource: source.source,
                    defaultAudio,
                    preferredAudioLangs: PREFERRED_AUDIO_LANGS,
                }),
            }),
    )

    const handleTimeUpdate = useEffectEvent(
        (currentTime: number, duration: number) => {
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
    const [frozenTimeStyle, setFrozenTimeStyle] = useState<
        CSSProperties | undefined
    >(undefined)
    const [isVideoLoading, setIsVideoLoading] = useState(true)
    const [suppressErrorDialog, setSuppressErrorDialog] = useState(false)

    const { data, isLoading, error } = useGetPlayServerMedia({
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

    useEffect(() => {
        if (!media) return
        let playInitiated = false

        media.onloadedmetadata = () => {
            if (resumeTimeRef.current !== undefined) {
                media.currentTime = resumeTimeRef.current
                resumeTimeRef.current = undefined
            }
        }
        media.oncanplay = () => {
            setIsVideoLoading(false)
            setSuppressErrorDialog(false)
            if (media.paused && !playInitiated) {
                // playInitiated is needed to prevent
                // play from being called twice which
                // currently causes the audio to bug and
                // play twice one audio source even
                // continues in the background after
                // the player is closed
                playInitiated = true
                media.play()
            }
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
        media.ontimeupdate = () => {
            const { currentTime, duration } = media
            if (!duration) return
            handleTimeUpdate(currentTime, duration)
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

    const capturePosition = () => {
        if (!media) return
        resumeTimeRef.current = media.currentTime
        const fill =
            media.duration > 0 ? (media.currentTime / media.duration) * 100 : 0
        setFrozenTimeStyle({
            '--media-slider-fill': `${fill}%`,
        } as CSSProperties)
        setIsVideoLoading(true)
    }

    const handleBitrateChange = (bitrate: number) => {
        if (bitrate >= source.source.bit_rate) {
            localStorage.removeItem('maxBitrate')
            setMaxBitrate(MAX_BITRATE)
        } else {
            localStorage.setItem('maxBitrate', String(bitrate))
            setMaxBitrate(bitrate)
        }
        capturePosition()
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
            timeSliderStyle={frozenTimeStyle}
            isVideoLoading={isVideoLoading}
            suppressErrorDialog={suppressErrorDialog}
            onSourceChange={(s) => {
                capturePosition()
                setSource(s)
            }}
            onBitrateChange={handleBitrateChange}
            onAudioChange={(audio) => {
                capturePosition()
                setAudioLang(audio)
                onAudioChange?.(audio)
            }}
            onForceTranscodeChange={(v) => {
                capturePosition()
                setForceTranscode(v)
            }}
            defaultSubtitle={activeSubtitle}
            onSubtitleChange={(s) => {
                setActiveSubtitle(s)
                onSubtitleChange?.(s)
            }}
            preferredAudioLangs={PREFERRED_AUDIO_LANGS}
            preferredSubtitleLangs={PREFERRED_SUBTITLE_LANGS}
            defaultStartTime={defaultStartTime}
        />
    )
}
