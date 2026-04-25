export type HDRType = 'hdr10' | 'hlg' | 'dovi'
export const HDR_FORMATS: HDRType[] = ['hdr10', 'hlg', 'dovi']
export const HDR_FORMAT_LABELS: Record<HDRType, string> = {
    hdr10: 'HDR10',
    hlg: 'HLG',
    dovi: 'Dolby Vision',
}

export type VideoCodec = 'av1' | 'h264' | 'hevc'
export const VIDEO_CODECS: VideoCodec[] = ['av1', 'h264', 'hevc']
export const VIDEO_CODEC_LABELS: Record<VideoCodec, string> = {
    av1: 'AV1',
    h264: 'H.264',
    hevc: 'H.265 / HEVC',
}

export type AudioCodec =
    | 'aac'
    | 'eac3'
    | 'ac3'
    | 'ac4'
    | 'opus'
    | 'flac'
    | 'dtsc'
    | 'dtse'
    | 'dtsx'
export const AUDIO_CODECS: AudioCodec[] = [
    'aac',
    'eac3',
    'ac3',
    'ac4',
    'opus',
    'flac',
    'dtsc',
    'dtse',
    'dtsx',
]
export const AUDIO_CODEC_LABELS: Record<AudioCodec, string> = {
    aac: 'AAC',
    eac3: 'DD+',
    ac3: 'Dolby Digital',
    ac4: 'Dolby AC-4',
    opus: 'Opus',
    flac: 'FLAC',
    dtsc: 'DTS Core',
    dtse: 'DTS Express',
    dtsx: 'DTS:X',
}

export const AUDIO_CODEC_CHECK_TYPE: { [key in AudioCodec]: string } = {
    aac: 'audio/mp4; codecs="aac"',
    eac3: 'audio/mp4; codecs="ec-3"',
    ac3: 'audio/mp4; codecs="ac-3"',
    ac4: 'audio/mp4; codecs="ac-4"',
    opus: 'audio/mp4; codecs="opus"',
    flac: 'audio/mp4; codecs="flac"',
    dtsc: 'audio/mp4; codecs="dtsc"',
    dtse: 'audio/mp4; codecs="dtse"',
    dtsx: 'audio/mp4; codecs="dtsx"',
} as const

export type VideoContainer = 'mp4' | 'webm'
export const VIDEO_CONTAINERS: VideoContainer[] = ['mp4', 'webm']

export type StreamFormat = 'hls'
export const STREAM_FORMATS: StreamFormat[] = ['hls']
