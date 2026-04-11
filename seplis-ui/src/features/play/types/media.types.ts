export type HDRType = 'hdr10' | 'hlg' | 'dovi'
export const HDR_FORMATS: HDRType[] = ['hdr10', 'hlg', 'dovi']

export type VideoCodec = 'av1' | 'h264' | 'hevc'
export const VIDEO_CODECS: VideoCodec[] = ['av1', 'h264', 'hevc']

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

export type VideoContainer = 'mp4' | 'webm'
export const VIDEO_CONTAINERS: VideoContainer[] = ['mp4', 'webm']

export type StreamFormat = 'hls'
export const STREAM_FORMATS: StreamFormat[] = ['hls']
