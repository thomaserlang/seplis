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
    PlaySourceStream,
} from '@/features/play/types/play-source.types'
import { PlayerProps } from '@/features/play/types/player.types'
import {
    pickStartAudio,
    pickStartSource,
    pickStartSubtitle,
    toLangKey,
} from '@/features/play/utils/play-source.utils'
import { Container, Paper } from '@mantine/core'
import { useEffect, useRef, useState } from 'react'
import { useChromecast } from '../providers/chromecast-provider'
import { ChromecastCapabilities } from '../types'
import { PlayerCast } from './player-cast'

interface Props extends PlayerProps {
    playRequestsSources: PlayRequestSources[]
}

const FALLBACK_CAPABILITIES: ChromecastCapabilities = {
    supportedVideoCodecs: ['h264'],
    supportedAudioCodecs: ['aac', 'opus', 'flac'],
    supportedVideoContainers: ['mp4'],
    supportedHdrFormats: [],
    hdrEnabled: false,
    maxAudioChannels: 2,
    maxWidth: 1920,
}

export function PlayerCastView({
    playRequestsSources,
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    defaultAudioKey,
    defaultSubtitleKey,
    defaultStartTime,
    onAudioChange,
    onSubtitleChange,
    castInfo,
}: Props) {
    const { capabilities } = useChromecast()
    const [capabilitiesTimedOut, setCapabilitiesTimedOut] = useState(false)

    useEffect(() => {
        if (capabilities) {
            setCapabilitiesTimedOut(false)
            return
        }

        const timeoutId = window.setTimeout(() => {
            setCapabilitiesTimedOut(true)
        }, 3000)

        return () => {
            window.clearTimeout(timeoutId)
        }
    }, [capabilities])

    const resolvedCapabilities =
        capabilities ?? (capabilitiesTimedOut ? FALLBACK_CAPABILITIES : null)

    return (
        <Container size="xs" pt="2rem">
            <Paper withBorder radius="1rem" p="1rem" bg="transparent">
                <PlayerCastViewReady
                    playRequestsSources={playRequestsSources}
                    title={title}
                    secondaryTitle={secondaryTitle}
                    onClose={onClose}
                    onPlayNext={onPlayNext}
                    defaultAudioKey={defaultAudioKey}
                    defaultSubtitleKey={defaultSubtitleKey}
                    defaultStartTime={defaultStartTime}
                    onAudioChange={onAudioChange}
                    onSubtitleChange={onSubtitleChange}
                    castInfo={castInfo}
                    capabilities={resolvedCapabilities ?? FALLBACK_CAPABILITIES}
                    shouldRequestMedia={resolvedCapabilities != null}
                    capabilitiesPending={resolvedCapabilities == null}
                />
            </Paper>
        </Container>
    )
}

interface ReadyProps extends Props {
    capabilities: ChromecastCapabilities
    shouldRequestMedia: boolean
    capabilitiesPending: boolean
}

function PlayerCastViewReady({
    playRequestsSources,
    title,
    secondaryTitle,
    onClose,
    onPlayNext,
    defaultAudioKey,
    defaultSubtitleKey,
    defaultStartTime,
    onAudioChange,
    onSubtitleChange,
    castInfo,
    capabilities,
    shouldRequestMedia,
    capabilitiesPending,
}: ReadyProps) {
    const { castSession, player: castPlayer, playbackError } = useChromecast()
    const playSettings = usePlaySettings('cast-settings', {
        supportedVideoCodecs: capabilities.supportedVideoCodecs,
        supportedAudioCodecs: capabilities.supportedAudioCodecs,
        transcodeVideoCodec: capabilities.supportedVideoCodecs[0] ?? 'h264',
        transcodeAudioCodec: capabilities.supportedAudioCodecs[0] ?? 'aac',
        supportedVideoContainers: capabilities.supportedVideoContainers,
        maxAudioChannels: capabilities.maxAudioChannels,
        supportedHdrFormats: capabilities.supportedHdrFormats,
        hdrEnabled: capabilities.hdrEnabled,
        maxWidth: capabilities.maxWidth,
    })
    const [source, setSource] = useState<PlayRequestSource>(() =>
        pickStartSource(playRequestsSources, playSettings.settings.maxBitrate),
    )
    const [audio, setAudioLang] = useState<PlaySourceStream | undefined>(
        pickStartAudio({
            playSource: source.source,
            defaultAudioKey: defaultAudioKey,
            preferredAudioLangs: PREFERRED_AUDIO_LANGS,
        }),
    )
    const [forceTranscode, setForceTranscode] = useState(false)
    const [subtitle, setSubtitle] = useState<PlaySourceStream | undefined>(() =>
        pickStartSubtitle({
            playSource: source.source,
            defaultSubtitleKey: defaultSubtitleKey,
            preferredSubtitleLangs: PREFERRED_SUBTITLE_LANGS,
            audio,
        }),
    )
    const canUseDirectPlay =
        source.source.format === 'mp4' &&
        source.source.media_type?.startsWith('video/mp4') === true

    const startTimeRef = useRef<number>(defaultStartTime ?? 0)
    const lastLoadedUrlRef = useRef<string | null>(null)

    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
        audio: toLangKey(audio),
        forceTranscode,
        ...playSettings.settings,
        options: {
            enabled: shouldRequestMedia,
            refetchOnWindowFocus: false,
            staleTime: 6 * 60 * 60 * 1000, // 6 hours
        },
    })

    useEffect(() => {
        if (!playbackError) return
        if (forceTranscode) return
        setForceTranscode(true)
    }, [playbackError, forceTranscode])

    useEffect(() => {
        if (!data || !castSession) return
        const contentUrl =
            data.can_direct_play && canUseDirectPlay && source.source.media_type
                ? data.direct_play_url
                : data.hls_url
        if (contentUrl === lastLoadedUrlRef.current) return
        lastLoadedUrlRef.current = contentUrl

        const subtitleTracks = source.source.subtitles.map((sub, i) => {
            const key = toLangKey(sub)
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
            contentUrl,
            data.can_direct_play && canUseDirectPlay && source.source.media_type
                ? source.source.media_type
                : 'application/x-mpegurl',
        )
        if (!(data.can_direct_play && canUseDirectPlay)) {
            // @ts-ignore
            mediaInfo.hlsVideoSegmentFormat = // @ts-ignore
                chrome.cast.media.HlsSegmentFormat.FMP4
        }
        ;(mediaInfo as any).contentUrl = contentUrl
        mediaInfo.streamType = chrome.cast.media.StreamType.BUFFERED
        mediaInfo.metadata = metadata
        mediaInfo.tracks = subtitleTracks

        const request = new chrome.cast.media.LoadRequest(mediaInfo)
        request.autoplay = true

        request.currentTime =
            castPlayer?.isMediaLoaded && (castPlayer.currentTime ?? 0) > 0
                ? castPlayer.currentTime
                : startTimeRef.current

        if (subtitle) {
            const idx = source.source.subtitles.findIndex(
                (s) => s.group_index === subtitle.group_index,
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
    }, [
        data,
        castSession,
        canUseDirectPlay,
        source.source.media_type,
        source.source.subtitles,
        source.request.play_id,
        source.request.play_url,
        source.source.index,
        title,
        secondaryTitle,
        castPlayer?.isMediaLoaded,
        castPlayer?.currentTime,
        subtitle,
        castInfo?.savePositionUrl,
        castInfo?.watchedUrl,
        source.source.duration,
    ])

    useEffect(() => {
        if (!castSession) return
        const mediaSession = castSession.getMediaSession()
        if (!mediaSession) return

        const activeTrackIds = (() => {
            if (!subtitle) return []
            const idx = source.source.subtitles.findIndex(
                (s) => s.group_index === subtitle.group_index,
            )
            return idx >= 0 ? [idx + 1] : []
        })()

        const req = new chrome.cast.media.EditTracksInfoRequest(activeTrackIds)
        mediaSession.editTracksInfo(
            req,
            () => {},
            () => {},
        )
    }, [subtitle, castSession])

    return (
        <>
            {capabilitiesPending && <PageLoader />}
            {!capabilitiesPending && isLoading && <PageLoader />}
            {!capabilitiesPending && error && <ErrorBox errorObj={error} />}
            {!capabilitiesPending && !data && !isLoading && (
                <ErrorBox message="No playable source found" />
            )}
            <PlayerCast
                title={title}
                secondaryTitle={secondaryTitle}
                onClose={onClose}
                onPlayNext={onPlayNext}
                playRequestSource={source}
                playRequestsSources={playRequestsSources}
                audio={audio}
                forceTranscode={forceTranscode}
                subtitle={subtitle}
                onSourceChange={setSource}
                onAudioChange={(a) => {
                    setAudioLang(a)
                    onAudioChange?.(a)
                }}
                onForceTranscodeChange={setForceTranscode}
                onSubtitleChange={(s) => {
                    setSubtitle(s)
                    onSubtitleChange?.(s)
                }}
                preferredAudioLangs={PREFERRED_AUDIO_LANGS}
                preferredSubtitleLangs={PREFERRED_SUBTITLE_LANGS}
                playSettings={playSettings}
            />
        </>
    )
}
