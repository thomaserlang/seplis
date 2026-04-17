import { use, useMemo, useState } from 'react'
import { MAX_BITRATE } from '../constants/play-bitrate.constants'
import {
    AudioCodec,
    HDRType,
    StreamFormat,
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

export interface PlaySettings {
    maxBitrate: number
    supportedVideoCodecs: VideoCodec[]
    supportedAudioCodecs: AudioCodec[]
    transcodeVideoCodec: VideoCodec
    transcodeAudioCodec: AudioCodec
    supportedVideoContainers: VideoContainer[]
    maxAudioChannels: number
    supportedHdrFormats: HDRType[]
    hdrEnabled: boolean
    format: StreamFormat
    defaultAudio?: string
    defaultSubtitle?: string
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
    const browserVideoCodecs = useMemo(() => getSupportedVideoCodecs(), [])
    const browserAudioCodecs = useMemo(() => getSupportedAudioCodecs(), [])
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
    const defaultAudioCodecs =
        defaults?.supportedAudioCodecs ?? browserAudioCodecs
    const defaultVideoContainers =
        defaults?.supportedVideoContainers ?? browserVideoContainers

    const videoCodecs = overrides.supportedVideoCodecs ?? defaultVideoCodecs
    const audioCodecs = overrides.supportedAudioCodecs ?? defaultAudioCodecs

    const defaultAudio = overrides.defaultAudio ?? defaults?.defaultAudio
    const defaultSubtitle =
        overrides.defaultSubtitle ?? defaults?.defaultSubtitle

    const settings: PlaySettings = {
        maxBitrate: overrides.maxBitrate ?? defaults?.maxBitrate ?? MAX_BITRATE,
        supportedVideoCodecs: videoCodecs,
        supportedAudioCodecs: audioCodecs,
        transcodeVideoCodec:
            overrides.transcodeVideoCodec ??
            defaults?.transcodeVideoCodec ??
            videoCodecs[0] ??
            'h264',
        transcodeAudioCodec:
            overrides.transcodeAudioCodec ??
            defaults?.transcodeAudioCodec ??
            'aac',
        supportedVideoContainers:
            overrides.supportedVideoContainers ?? defaultVideoContainers,
        maxAudioChannels:
            overrides.maxAudioChannels ?? defaults?.maxAudioChannels ?? 6,
        format: overrides.format ?? defaults?.format ?? 'hls',
        supportedHdrFormats:
            overrides.supportedHdrFormats ??
            defaults?.supportedHdrFormats ??
            browserHdrTypes,
        hdrEnabled:
            overrides.hdrEnabled ?? defaults?.hdrEnabled ?? getHdrSupport(),
        defaultAudio,
        defaultSubtitle,
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
