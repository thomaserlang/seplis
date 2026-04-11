import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useGetPlayServerMedia } from '@/features/play/api/play-server-request-media.api'
import {
    PREFERRED_AUDIO_LANGS,
    PREFERRED_SUBTITLE_LANGS,
} from '@/features/play/constants/play-language.constants'
import { usePlaySettings } from '@/features/play/hooks/use-play-settings'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '@/features/play/types/play-source.types'
import { PlayerProps } from '@/features/play/types/player.types'
import {
    pickStartAudio,
    pickStartSource,
    pickStartSubtitle,
} from '@/features/play/utils/play-source.utils'
import { Container, Paper } from '@mantine/core'
import { useEffect, useRef, useState } from 'react'
import { useChromecast } from '../providers/chromecast-provider'
import { PlayerCast } from './player-cast'

interface Props extends PlayerProps {
    playRequestsSources: PlayRequestSources[]
}

export function PlayerCastView({
    playRequestsSources,
    title,
    secondaryTitle,
    onClose,
    defaultAudio,
    defaultSubtitle,
    defaultStartTime,
    onAudioChange,
    onSubtitleChange,
    castInfo,
}: Props) {
    const playSettings = usePlaySettings('cast-settings', {
        supportedVideoCodecs: ['h264'],
        supportedAudioCodecs: ['aac', 'opus', 'flac'],
        transcodeVideoCodec: 'h264',
        transcodeAudioCodec: 'aac',
        supportedVideoContainers: ['mp4'],
        maxAudioChannels: 2,
    })
    const { castSession, player: castPlayer } = useChromecast()
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

    const startTimeRef = useRef<number>(defaultStartTime ?? 0)
    const lastLoadedUrlRef = useRef<string | null>(null)

    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
        audio,
        forceTranscode,
        ...playSettings.settings,
        options: {
            refetchOnWindowFocus: false,
            staleTime: 6 * 60 * 60 * 1000, // 6 hours
        },
    })

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
        ;(mediaInfo as any).contentUrl = data.hls_url
        mediaInfo.streamType = chrome.cast.media.StreamType.BUFFERED
        mediaInfo.metadata = metadata
        mediaInfo.tracks = subtitleTracks

        const request = new chrome.cast.media.LoadRequest(mediaInfo)
        request.autoplay = true

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

        request.customData = {
            keep_alive_url: data.keep_alive_url,
            save_position_url: castInfo?.savePositionUrl,
            watched_url: castInfo?.watchedUrl,
            token: localStorage.getItem('accessToken'),
            duration: source.source.duration,
        }

        castSession.loadMedia(request)
    }, [data, castSession])

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
    }, [activeSubtitleKey, castSession])

    return (
        <Container size="xs" pt="2rem">
            <Paper withBorder radius="1rem" p="1rem" bg="transparent">
                {isLoading && <PageLoader />}
                {error && <ErrorBox errorObj={error} />}
                {!data && !isLoading && (
                    <ErrorBox message="No playable source found" />
                )}
                {data && (
                    <PlayerCast
                        title={title}
                        secondaryTitle={secondaryTitle}
                        onClose={onClose}
                        playRequestSource={source}
                        playRequestsSources={playRequestsSources}
                        audio={audio}
                        forceTranscode={forceTranscode}
                        activeSubtitleKey={activeSubtitleKey}
                        onSourceChange={setSource}
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
                        playSettings={playSettings}
                    />
                )}
            </Paper>
        </Container>
    )
}
