import {
    AUDIO_CODEC_LABELS,
    VIDEO_CODEC_LABELS,
} from '../constants/media.constants'

const VIDEO_CODEC_ALIASES: Record<string, string> = {
    h265: VIDEO_CODEC_LABELS.hevc,
    vp8: 'VP8',
    vp9: 'VP9',
}

const AUDIO_CODEC_ALIASES: Record<string, string> = {
    truehd: 'Dolby TrueHD',
}

export function videoCodecLabel(codec: string | null | undefined): string {
    return codecLabel(codec, VIDEO_CODEC_LABELS, VIDEO_CODEC_ALIASES)
}

export function audioCodecLabel(codec: string | null | undefined): string {
    return codecLabel(codec, AUDIO_CODEC_LABELS, AUDIO_CODEC_ALIASES)
}

function codecLabel(
    codec: string | null | undefined,
    labels: Record<string, string>,
    aliases: Record<string, string>,
): string {
    const value = codec?.trim()
    if (!value) return 'unknown'

    const normalized = value.toLowerCase()
    return labels[normalized] ?? aliases[normalized] ?? value.toUpperCase()
}
