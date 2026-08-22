import { useOs } from '@mantine/hooks'
import { use, useMemo, useState } from 'react'
import {
    AUDIO_CODECS,
    TRANSCODE_AUDIO_CODECS,
} from '../constants/media.constants'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import type {
    AudioCodec,
    HDRType,
    StreamFormat,
    TranscodeAudioCodec,
    VideoCodec,
    VideoContainer,
} from '../types/media.types'
import {
    getHdrSupport,
    getSupportedAudioCodecs,
    getSupportedHDRTypes,
    getSupportedVideoCodecs,
    getSupportedVideoContainers,
} from '../utils/video.utils'

const hdrTypesPromise = getSupportedHDRTypes()
let videoCodecsPromise: Promise<VideoCodec[]> | null = null

function loadVideoCodecs() {
    if (videoCodecsPromise === null) {
        videoCodecsPromise = getSupportedVideoCodecs()
    }
    return videoCodecsPromise
}

export interface PlaySettings {
    maxBitrate: number
    maxWidth?: number
    supportedVideoCodecs: VideoCodec[]
    supportedVideoColorBitDepth: number
    supportedAudioCodecs: AudioCodec[]
    transcodeVideoCodec: VideoCodec
    transcodeAudioCodec: TranscodeAudioCodec
    supportedVideoContainers: VideoContainer[]
    maxAudioChannels: number
    supportedHdrFormats: HDRType[]
    hdrEnabled: boolean
    format: StreamFormat
    defaultAudioKey?: string
    defaultSubtitleKey?: string
}

export interface PlaySettingsOverrides extends Partial<PlaySettings> {}

export interface UsePlaySettings {
    settings: PlaySettings
    overrides: PlaySettingsOverrides
    update: (changes: Partial<PlaySettingsOverrides>) => void
    reset: () => void
    isDefault: boolean
}

export function usePlaySettings(
    storageKey: string,
    defaults?: Partial<PlaySettings>,
): UsePlaySettings {
    const os = useOs({ getValueInEffect: false })
    const isAppleMobileDevice = os === 'ios'
    const browserVideoCodecs = use(loadVideoCodecs())
    const browserAudioCodecs = useMemo(
        () => getSupportedAudioCodecs(isAppleMobileDevice),
        [isAppleMobileDevice],
    )
    const browserVideoContainers = useMemo(
        () => getSupportedVideoContainers(),
        [],
    )
    const browserHdrTypes = use(hdrTypesPromise)

    const [overrides, setOverrides] = useState<PlaySettingsOverrides>(() => {
        try {
            return JSON.parse(localStorage.getItem(storageKey) ?? '{}')
        } catch {
            return {}
        }
    })

    const defaultVideoCodecs =
        defaults?.supportedVideoCodecs ?? browserVideoCodecs
    const defaultAudioCodecs = normalizeAudioCodecs(
        defaults?.supportedAudioCodecs ?? browserAudioCodecs,
    )
    const defaultVideoContainers =
        defaults?.supportedVideoContainers ?? browserVideoContainers

    const videoCodecs = overrides.supportedVideoCodecs ?? defaultVideoCodecs
    const audioCodecs = normalizeAudioCodecs(
        overrides.supportedAudioCodecs ?? defaultAudioCodecs,
    )
    const requestedTranscodeAudioCodec =
        overrides.transcodeAudioCodec ?? defaults?.transcodeAudioCodec
    const transcodeAudioCodec = isTranscodeAudioCodec(
        requestedTranscodeAudioCodec,
    )
        ? requestedTranscodeAudioCodec
        : (TRANSCODE_AUDIO_CODECS.find((codec) =>
              audioCodecs.includes(codec),
          ) ?? 'aac')

    const defaultAudioKey =
        overrides.defaultAudioKey ?? defaults?.defaultAudioKey
    const defaultSubtitleKey =
        overrides.defaultSubtitleKey ?? defaults?.defaultSubtitleKey

    const settings: PlaySettings = {
        maxBitrate: overrides.maxBitrate ?? defaults?.maxBitrate ?? MAX_BITRATE,
        maxWidth: overrides.maxWidth ?? defaults?.maxWidth,
        supportedVideoCodecs: videoCodecs,
        supportedVideoColorBitDepth:
            overrides.supportedVideoColorBitDepth ??
            defaults?.supportedVideoColorBitDepth ??
            8,
        supportedAudioCodecs: audioCodecs,
        transcodeVideoCodec:
            overrides.transcodeVideoCodec ??
            defaults?.transcodeVideoCodec ??
            videoCodecs[0] ??
            'h264',
        transcodeAudioCodec: transcodeAudioCodec,
        supportedVideoContainers:
            overrides.supportedVideoContainers ?? defaultVideoContainers,
        maxAudioChannels:
            overrides.maxAudioChannels ??
            defaults?.maxAudioChannels ??
            (isAppleMobileDevice ? 8 : 6),
        format: overrides.format ?? defaults?.format ?? 'hls',
        supportedHdrFormats:
            overrides.supportedHdrFormats ??
            defaults?.supportedHdrFormats ??
            browserHdrTypes,
        hdrEnabled:
            overrides.hdrEnabled ?? defaults?.hdrEnabled ?? getHdrSupport(),
        defaultAudioKey: defaultAudioKey,
        defaultSubtitleKey: defaultSubtitleKey,
    }

    const update = (changes: Partial<PlaySettingsOverrides>) => {
        const next: PlaySettingsOverrides = { ...overrides }
        for (const [k, v] of Object.entries(changes)) {
            if (v === undefined) {
                delete next[k as keyof PlaySettingsOverrides]
            } else {
                ;(next as Record<string, unknown>)[k] = v
            }
        }

        setOverrides(next)
        if (Object.keys(next).length === 0) {
            localStorage.removeItem(storageKey)
        } else {
            localStorage.setItem(storageKey, JSON.stringify(next))
        }
    }

    const reset = () => {
        setOverrides({})
        localStorage.removeItem(storageKey)
    }

    const isDefault = Object.keys(overrides).length === 0

    return {
        settings,
        overrides,
        update,
        reset,
        isDefault,
    }
}

function normalizeAudioCodecs(codecs: unknown): AudioCodec[] {
    if (!Array.isArray(codecs)) return []

    const normalized = codecs.filter(
        (codec): codec is AudioCodec =>
            typeof codec === 'string' &&
            AUDIO_CODECS.includes(codec as AudioCodec),
    )

    return [...new Set(normalized)]
}

function isTranscodeAudioCodec(codec: unknown): codec is TranscodeAudioCodec {
    return TRANSCODE_AUDIO_CODECS.includes(codec as TranscodeAudioCodec)
}
