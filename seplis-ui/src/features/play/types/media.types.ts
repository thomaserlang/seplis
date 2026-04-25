import type {
    AUDIO_CODECS,
    HDR_FORMATS,
    STREAM_FORMATS,
    VIDEO_CODECS,
    VIDEO_CONTAINERS,
} from '../constants/media.constants'

export type HDRType = (typeof HDR_FORMATS)[number]

export type VideoCodec = (typeof VIDEO_CODECS)[number]

export type AudioCodec = (typeof AUDIO_CODECS)[number]

export type VideoContainer = (typeof VIDEO_CONTAINERS)[number]

export type StreamFormat = (typeof STREAM_FORMATS)[number]
