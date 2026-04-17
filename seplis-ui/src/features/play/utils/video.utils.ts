import {
    AudioCodec,
    HDRType,
    VideoCodec,
    VideoContainer,
} from '../types/media.types'

export function getSupportedVideoCodecs(): VideoCodec[] {
    const video = document.createElement('video')
    const types: { [key: string]: VideoCodec } = {
        'video/mp4; codecs="hvc1"': 'hevc',
        'video/mp4; codecs="hev1.1.6.L93.90"': 'hevc',
        'video/mp4; codecs="av01.0.08M.08"': 'av1',
        'video/mp4; codecs="avc1.42E01E"': 'h264',
    }
    const codecs: VideoCodec[] = []
    for (const key in types) if (video.canPlayType(key)) codecs.push(types[key])
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
    const containers: { [key: string]: VideoContainer } = {
        'video/mp4': 'mp4',
    }
    if (!isSafari) {
        containers['video/webm'] = 'webm' // TODO: safari gives issues with byte ranges
    }
    return Object.entries(containers)
        .filter(([mime]) => video.canPlayType(mime))
        .map(([, name]) => name)
}

export function getSupportedAudioCodecs(): AudioCodec[] {
    const video = document.createElement('video')
    const types: { [key: string]: AudioCodec } = {
        'audio/aac': 'aac',
        'audio/mp4; codecs="ec-3"': 'eac3',
        'audio/mp4; codecs="ac-3"': 'ac3',
        'audio/mp4; codecs="ac-4"': 'ac4',
        'audio/mp4; codecs="opus"': 'opus',
        'audio/mp4; codecs="flac"': 'flac',
        'audio/mp4; codecs="dtsc"': 'dtsc',
        'audio/mp4; codecs="dtse"': 'dtse',
        'audio/mp4; codecs="dtsx"': 'dtsx',
    }
    const codecs: AudioCodec[] = []
    for (const key in types) if (video.canPlayType(key)) codecs.push(types[key])
    return [...new Set(codecs)]
}
