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
import {
    createChromecastLoadRequest,
    getSubtitleTrackIds,
} from '../utils/chromecast-load-request'
import {
    getCastMediaKey,
    getCastVariantKey,
    getCurrentCastMediaIdentity,
    type SeplisCastMediaIdentity,
} from '../utils/chromecast-media-identity'
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
    const {
        castSession,
        sessionState,
        mediaSession,
        player: castPlayer,
        playbackError,
        loadError,
        loadMedia,
        editTracks,
    } = useChromecast()
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
    const lastLoadedKeyRef = useRef<string | null>(null)
    const inFlightLoadKeyRef = useRef<string | null>(null)
    const [resumeMediaCheckTimedOut, setResumeMediaCheckTimedOut] =
        useState(false)

    const castSessionId = castSession?.getSessionId() ?? null
    const castMediaKey = getCastMediaKey(source)
    const castVariantKey = getCastVariantKey({
        source,
        audio,
        forceTranscode,
        settings: playSettings.settings,
    })
    const remoteMediaIdentity = getCurrentCastMediaIdentity({
        mediaSession,
        castPlayer,
    })
    const isAttachedToCurrentCastMedia =
        remoteMediaIdentity?.mediaKey === castMediaKey &&
        remoteMediaIdentity.variantKey === castVariantKey
    const hasRemoteMediaStatus =
        mediaSession?.media != null ||
        castPlayer?.isMediaLoaded === true ||
        castPlayer?.mediaInfo != null
    const shouldWaitForResumedMedia =
        sessionState === 'SESSION_RESUMED' &&
        !resumeMediaCheckTimedOut &&
        !isAttachedToCurrentCastMedia &&
        (!hasRemoteMediaStatus || remoteMediaIdentity == null)

    useEffect(() => {
        setResumeMediaCheckTimedOut(false)
        if (sessionState !== 'SESSION_RESUMED') return

        const timeoutId = window.setTimeout(() => {
            setResumeMediaCheckTimedOut(true)
        }, 2000)

        return () => {
            window.clearTimeout(timeoutId)
        }
    }, [castSessionId, sessionState])

    const { data, isLoading, error } = useGetPlayServerMedia({
        playRequestSource: source,
        audio: toLangKey(audio),
        forceTranscode,
        ...playSettings.settings,
        options: {
            enabled:
                shouldRequestMedia &&
                !isAttachedToCurrentCastMedia &&
                !shouldWaitForResumedMedia,
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
        if (isAttachedToCurrentCastMedia) {
            lastLoadedKeyRef.current = castVariantKey
            inFlightLoadKeyRef.current = null
            return
        }
        if (shouldWaitForResumedMedia) return
        if (!data || !castSession) return
        const contentUrl =
            data.can_direct_play && canUseDirectPlay && source.source.media_type
                ? data.direct_play_url
                : data.hls_url
        const loadKey = [contentUrl, castVariantKey].join('|')
        if (
            loadKey === lastLoadedKeyRef.current ||
            loadKey === inFlightLoadKeyRef.current
        ) {
            return
        }
        inFlightLoadKeyRef.current = loadKey

        const directPlayContentType =
            data.can_direct_play && canUseDirectPlay
                ? (source.source.media_type ?? undefined)
                : undefined
        const seplisCastIdentity: SeplisCastMediaIdentity = {
            version: 1,
            mediaKey: castMediaKey,
            variantKey: castVariantKey,
        }
        const remoteCurrentTime =
            castPlayer?.isMediaLoaded &&
            remoteMediaIdentity?.mediaKey === castMediaKey &&
            (castPlayer.currentTime ?? 0) > 0
                ? castPlayer.currentTime
                : null

        const request = createChromecastLoadRequest({
            source,
            contentUrl,
            directPlayContentType,
            title,
            secondaryTitle,
            subtitle,
            currentTime: remoteCurrentTime ?? startTimeRef.current,
            seplisCastIdentity,
            customData: {
                keep_alive_url: data.keep_alive_url,
                save_position_url: castInfo?.savePositionUrl,
                watched_url: castInfo?.watchedUrl,
                token: localStorage.getItem('accessToken'),
                duration: source.source.duration,
            },
        })

        loadMedia(request)
            .then(() => {
                if (inFlightLoadKeyRef.current === loadKey) {
                    lastLoadedKeyRef.current = loadKey
                }
            })
            .catch(() => {
                if (inFlightLoadKeyRef.current === loadKey) {
                    lastLoadedKeyRef.current = null
                }
            })
            .finally(() => {
                if (inFlightLoadKeyRef.current === loadKey) {
                    inFlightLoadKeyRef.current = null
                }
            })
    }, [
        data,
        castSession,
        loadMedia,
        isAttachedToCurrentCastMedia,
        shouldWaitForResumedMedia,
        canUseDirectPlay,
        castMediaKey,
        castVariantKey,
        source.source.media_type,
        source.source.subtitles,
        source.request.play_id,
        source.request.play_url,
        source.source.index,
        audio,
        forceTranscode,
        title,
        secondaryTitle,
        castPlayer?.isMediaLoaded,
        castPlayer?.currentTime,
        remoteMediaIdentity?.mediaKey,
        subtitle,
        castInfo?.savePositionUrl,
        castInfo?.watchedUrl,
        source.source.duration,
    ])

    useEffect(() => {
        if (!mediaSession) return

        const activeTrackIds = getSubtitleTrackIds(
            source.source.subtitles,
            subtitle,
        )
        editTracks(activeTrackIds).catch(() => {})
    }, [subtitle, mediaSession, editTracks, source.source.subtitles])

    return (
        <>
            {capabilitiesPending && <PageLoader />}
            {!capabilitiesPending && shouldWaitForResumedMedia && (
                <PageLoader />
            )}
            {!capabilitiesPending &&
                !isAttachedToCurrentCastMedia &&
                isLoading && <PageLoader />}
            {!capabilitiesPending && error && <ErrorBox errorObj={error} />}
            {!capabilitiesPending &&
                !isAttachedToCurrentCastMedia &&
                loadError && <ErrorBox errorObj={loadError} />}
            {!capabilitiesPending &&
                !isAttachedToCurrentCastMedia &&
                !shouldWaitForResumedMedia &&
                !data &&
                !isLoading && <ErrorBox message="No playable source found" />}
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
