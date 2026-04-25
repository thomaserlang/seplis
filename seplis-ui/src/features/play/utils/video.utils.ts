import {
    AUDIO_CODEC_CHECK_TYPE,
    AudioCodec,
    HDRType,
    VideoCodec,
    VideoContainer,
} from '../types/media.types'

const VIDEO_CODEC_TYPES: Record<string, VideoCodec> = {
    'video/mp4; codecs="hvc1"': 'hevc',
    'video/mp4; codecs="hev1.1.6.L93.90"': 'hevc',
    'video/mp4; codecs="av01.0.08M.08"': 'av1',
    'video/mp4; codecs="avc1.42E01E"': 'h264',
}

async function hasSmoothMediaDecodingSupport(contentType: string) {
    if (!('mediaCapabilities' in navigator)) return true

    try {
        const result = await navigator.mediaCapabilities.decodingInfo({
            type: 'media-source',
            video: {
                contentType,
                width: 1920,
                height: 1080,
                framerate: 24,
                bitrate: 8_000_000,
            },
        })

        return result.supported && result.smooth
    } catch {
        return false
    }
}

export function canPlayMediaType(
    mediaType: string,
    kind: 'video' | 'audio' = 'video',
) {
    const media = document.createElement(kind)
    return !!media.canPlayType(mediaType)
}

export async function getSupportedVideoCodecs(): Promise<VideoCodec[]> {
    const video = document.createElement('video')
    const codecs = Object.entries(VIDEO_CODEC_TYPES)
        .filter(([mime]) => video.canPlayType(mime))
        .map(([, codec]) => codec)

    if (codecs.includes('av1')) {
        const av1Supported = await hasSmoothMediaDecodingSupport(
            'video/mp4; codecs="av01.0.08M.08"',
        )
        if (!av1Supported) {
            return codecs.filter((codec) => codec !== 'av1')
        }
    }

    return [...new Set(codecs)]
}

export function getHdrSupport() {
    return window.matchMedia('(dynamic-range: high)').matches
}

export async function getSupportedHDRTypes(): Promise<HDRType[]> {
    if (!('mediaCapabilities' in navigator)) return []

    const check = (codec: string, transfer: TransferFunction) =>
        navigator.mediaCapabilities
            .decodingInfo({
                type: 'media-source',
                video: {
                    contentType: `video/mp4; codecs="${codec}"`,
                    width: 3840,
                    height: 2160,
                    framerate: 30,
                    bitrate: 20_000_000,
                    transferFunction: transfer,
                },
            })
            .then((r) => r.supported)
            .catch(() => false)

    const checks: [HDRType, string, TransferFunction][] = [
        ['dovi', 'dvh1.05.07', 'pq'],
        ['hdr10', 'hev1.2.4.L153.B0', 'pq'],
        ['hlg', 'hev1.2.4.L153.B0', 'hlg'],
    ]

    const results = await Promise.all(
        checks.map(([, codec, transfer]) => check(codec, transfer)),
    )

    return checks.filter((_, i) => results[i]).map(([name]) => name)
}

export function getSupportedVideoContainers(): VideoContainer[] {
    const video = document.createElement('video')
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
    const isFirefox = /firefox/i.test(navigator.userAgent)

    const hasWebmByteRangeIssues = isSafari || isFirefox

    const containers: { [key: string]: VideoContainer } = {
        'video/mp4': 'mp4',
    }
    if (!hasWebmByteRangeIssues) {
        containers['video/webm'] = 'webm'
    }
    return Object.entries(containers)
        .filter(([mime]) => video.canPlayType(mime))
        .map(([, name]) => name)
}

export function getSupportedAudioCodecs(): AudioCodec[] {
    const video = document.createElement('video')

    const codecs: AudioCodec[] = []
    for (const [codec, mimeType] of Object.entries(AUDIO_CODEC_CHECK_TYPE) as [
        AudioCodec,
        string,
    ][]) {
        if (video.canPlayType(mimeType)) codecs.push(codec)
    }
    return [...new Set(codecs)]
}
