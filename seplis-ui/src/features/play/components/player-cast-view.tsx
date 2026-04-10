import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerCast } from '@/features/play/components/chromecast/components/player-cast'
import { useChromecast } from '@/features/play/components/chromecast/providers/chromecast-provider'
import { useEffect, useRef, useState } from 'react'
import { useGetPlayServerMedia } from '../api/play-server-media.api'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import {
    PREFERRED_AUDIO_LANGS,
    PREFERRED_SUBTITLE_LANGS,
} from '../constants/play-language.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'
import { PlayerProps } from '../types/player.types'
import { getDefaultMaxBitrate } from '../utils/play-bitrate.utils'
import {
    pickStartAudio,
    pickStartSource,
    pickStartSubtitle,
} from '../utils/play-source.utils'
import {
    CHROMECAST_SUPPORTED_AUDIO_CODECS,
    CHROMECAST_SUPPORTED_VIDEO_CODECS,
    CHROMECAST_SUPPORTED_VIDEO_CONTAINERS,
    CHROMECAST_TRANSCODE_AUDIO_CODEC,
    CHROMECAST_TRANSCODE_VIDEO_CODEC,
} from '../utils/video.utils'

import { Container, Paper } from '@mantine/core'
import './player-video.css'

interface Props extends PlayerProps {
    playRequestsSources: PlayRequestSources[]
}

export function PlayerCastView({
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
    const { castSession, player: castPlayer } = useChromecast()

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
    const [activeSubtitleKey, setActiveSubtitleKey] = useState<
        string | undefined
    >(() =>
        pickStartSubtitle({
            playSource: source.source,
            defaultSubtitle,
            preferredSubtitleLangs: PREFERRED_SUBTITLE_LANGS,
            audio,
        }),
    )

    const [castError, setCastError] = useState<string | null>(null)

    const startTimeRef = useRef<number>(defaultStartTime ?? 0)
    const lastSaveTimeRef = useRef<number>(defaultStartTime ?? 0)
    const finishedFiredRef = useRef(false)
    // Track the last URL sent so we reload even when React Query returns the
    // same cached object reference (e.g. settings changed back to a prior value).
    const lastLoadedUrlRef = useRef<string | null>(null)

    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
        maxBitrate: maxBitrate < MAX_BITRATE ? maxBitrate : undefined,
        audio,
        forceTranscode,
        supportedVideoCodecs: CHROMECAST_SUPPORTED_VIDEO_CODECS,
        supportedAudioCodecs: CHROMECAST_SUPPORTED_AUDIO_CODECS,
        transcodeVideoCodec: CHROMECAST_TRANSCODE_VIDEO_CODEC,
        transcodeAudioCodec: CHROMECAST_TRANSCODE_AUDIO_CODEC,
        supportedVideoContainers: CHROMECAST_SUPPORTED_VIDEO_CONTAINERS,
        options: {
            refetchOnWindowFocus: false,
            staleTime: Infinity,
        },
    })

    // Keep the play server session alive while casting.
    useEffect(() => {
        if (!data) return
        const id = setInterval(() => {
            fetch(data.keep_alive_url).catch(() => {})
        }, 5000)
        return () => clearInterval(id)
    }, [data?.keep_alive_url])

    // Track cast playback position for save-position and finished callbacks.
    useEffect(() => {
        if (!castPlayer) return
        const currentTime = castPlayer.currentTime ?? 0
        const duration = castPlayer.duration ?? 0
        if (finishedFiredRef.current || duration === 0) return
        if (currentTime >= duration * 0.9) {
            finishedFiredRef.current = true
            onFinished?.()
        } else if (currentTime - lastSaveTimeRef.current >= 10) {
            lastSaveTimeRef.current = currentTime
            onSavePosition?.(Math.round(currentTime))
        }
    })

    // Load (or reload) media on the cast device whenever the resolved URL
    // changes, resuming at the current playback position.
    useEffect(() => {
        if (!data || !castSession) return
        if (data.hls_url === lastLoadedUrlRef.current) return
        lastLoadedUrlRef.current = data.hls_url

        const subtitleTracks = source.source.subtitles.map((sub, i) => {
            const key = `${sub.language}:${sub.index}`
            const subtitleUrl =
                `${source.request.play_url}/subtitle-file` +
                `?play_id=${source.request.play_id}` +
                `&source_index=${source.source.index}` +
                `&lang=${key}`
            const track = new chrome.cast.media.Track(
                i + 1,
                chrome.cast.media.TrackType.TEXT,
            )
            track.trackContentId = subtitleUrl
            track.trackContentType = 'text/vtt'
            track.subtype = chrome.cast.media.TextTrackType.SUBTITLES
            track.name = sub.title || sub.language
            track.language = sub.language
            return track
        })

        const metadata = new chrome.cast.media.GenericMediaMetadata()
        metadata.title = title ?? ''
        metadata.subtitle = secondaryTitle ?? ''

        const mediaInfo = new chrome.cast.media.MediaInfo(
            data.hls_url,
            'application/x-mpegurl',
        )
        // @ts-ignore
        mediaInfo.hlsVideoSegmentFormat = // @ts-ignore
            chrome.cast.media.HlsSegmentFormat.FMP4
        // CAF receivers require contentUrl for actual playback;
        // contentId alone is treated as an opaque identifier.
        ;(mediaInfo as any).contentUrl = data.hls_url
        mediaInfo.streamType = chrome.cast.media.StreamType.BUFFERED
        mediaInfo.metadata = metadata
        mediaInfo.tracks = subtitleTracks

        const request = new chrome.cast.media.LoadRequest(mediaInfo)
        request.autoplay = true
        // Resume at the cast player's current time when already playing,
        // otherwise use the start time from props.
        request.currentTime =
            castPlayer?.isMediaLoaded && (castPlayer.currentTime ?? 0) > 0
                ? castPlayer.currentTime
                : startTimeRef.current

        if (activeSubtitleKey) {
            const idx = source.source.subtitles.findIndex(
                (s) => `${s.language}:${s.index}` === activeSubtitleKey,
            )
            if (idx >= 0) request.activeTrackIds = [idx + 1]
        }

        setCastError(null)
        castSession
            .loadMedia(request)
            .then((errorCode) => {
                if (errorCode) {
                    const msg = `loadMedia error: ${errorCode}`
                    console.error('[Cast]', msg)
                    setCastError(msg)
                }
            })
            .catch((err) => {
                const msg = `loadMedia failed: ${err}`
                console.error('[Cast]', msg)
                setCastError(msg)
            })
    }, [data, castSession]) // eslint-disable-line react-hooks/exhaustive-deps

    // Switch subtitle track on the cast device on the fly without reloading.
    useEffect(() => {
        if (!castSession) return
        const mediaSession = castSession.getMediaSession()
        if (!mediaSession) return

        const activeTrackIds = (() => {
            if (!activeSubtitleKey) return []
            const idx = source.source.subtitles.findIndex(
                (s) => `${s.language}:${s.index}` === activeSubtitleKey,
            )
            return idx >= 0 ? [idx + 1] : []
        })()

        const req = new chrome.cast.media.EditTracksInfoRequest(activeTrackIds)
        mediaSession.editTracksInfo(
            req,
            () => {},
            () => {},
        )
    }, [activeSubtitleKey, castSession]) // eslint-disable-line react-hooks/exhaustive-deps

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
        <Container size="xs" pt="2rem">
            <Paper withBorder radius="1rem" p="1rem" bg="transparent">
                <PlayerCast
                    title={title}
                    secondaryTitle={secondaryTitle}
                    onClose={onClose}
                    playRequestSource={source}
                    playRequestsSources={playRequestsSources}
                    maxBitrate={maxBitrate}
                    audio={audio}
                    forceTranscode={forceTranscode}
                    activeSubtitleKey={activeSubtitleKey}
                    onSourceChange={setSource}
                    onBitrateChange={handleBitrateChange}
                    onAudioChange={(a) => {
                        setAudioLang(a)
                        onAudioChange?.(a)
                    }}
                    onForceTranscodeChange={setForceTranscode}
                    onSubtitleChange={(s) => {
                        setActiveSubtitleKey(s)
                        onSubtitleChange?.(s)
                    }}
                    preferredAudioLangs={PREFERRED_AUDIO_LANGS}
                    preferredSubtitleLangs={PREFERRED_SUBTITLE_LANGS}
                />
            </Paper>
        </Container>
    )
}
