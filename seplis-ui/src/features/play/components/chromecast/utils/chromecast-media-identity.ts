import type { PlaySettings } from '@/features/play/hooks/use-play-settings'
import type {
    PlayRequestSource,
    PlaySourceStream,
} from '@/features/play/types/play-source.types'
import { toLangKey } from '@/features/play/utils/play-source.utils'

export interface SeplisCastMediaIdentity {
    version: 1
    mediaKey: string
    variantKey: string
}

function isRecord(value: unknown): value is Record<string, unknown> {
    return typeof value === 'object' && value !== null
}

export function getCastMediaKey(source: PlayRequestSource) {
    return `${source.request.play_id}:${source.source.index}`
}

export function getCastVariantKey({
    source,
    audio,
    forceTranscode,
    settings,
}: {
    source: PlayRequestSource
    audio?: PlaySourceStream
    forceTranscode: boolean
    settings: PlaySettings
}) {
    return JSON.stringify([
        getCastMediaKey(source),
        toLangKey(audio) ?? '',
        forceTranscode,
        settings.maxBitrate,
        settings.maxWidth ?? null,
        settings.maxAudioChannels,
        settings.supportedVideoCodecs,
        settings.supportedAudioCodecs,
        settings.transcodeVideoCodec,
        settings.transcodeAudioCodec,
        settings.supportedVideoContainers,
        settings.format,
        settings.supportedHdrFormats,
        settings.hdrEnabled,
    ])
}

export function getSeplisCastMediaIdentity(
    customData: unknown,
): SeplisCastMediaIdentity | null {
    if (!isRecord(customData)) return null
    const seplis = customData.seplis
    if (!isRecord(seplis)) return null

    if (
        seplis.version === 1 &&
        typeof seplis.mediaKey === 'string' &&
        typeof seplis.variantKey === 'string'
    ) {
        return {
            version: 1,
            mediaKey: seplis.mediaKey,
            variantKey: seplis.variantKey,
        }
    }

    return null
}

export function getCurrentCastMediaIdentity({
    mediaSession,
    castPlayer,
}: {
    mediaSession: chrome.cast.media.Media | null
    castPlayer: cast.framework.RemotePlayer | null
}) {
    return (
        getSeplisCastMediaIdentity(mediaSession?.media?.customData) ??
        getSeplisCastMediaIdentity(castPlayer?.mediaInfo?.customData) ??
        getSeplisCastMediaIdentity(mediaSession?.customData)
    )
}
