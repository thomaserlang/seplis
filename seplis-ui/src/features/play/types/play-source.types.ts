import { PlayRequest } from './play-request.types'
import { TranscodeDecision } from './transcode-decision.types'

export interface PlaySourceStream {
    title: string
    language: string
    index: number
    group_index: number | null
    codec: string | null
    forced: boolean
    default: boolean
    channels: number | null
}

export interface PlaySource {
    width: number
    height: number
    codec: string
    duration: number
    resolution: string
    audio: PlaySourceStream[]
    subtitles: PlaySourceStream[]
    video_color_range: string
    video_color_range_type: string
    index: number
    size: number
    bitrate: number
    format: string
    media_type: string | null
    fps: number
    pixel_format: string
    color_transfer: string
    color_primaries: string
}

export interface PlayRequestSource {
    request: PlayRequest
    source: PlaySource
}

export interface PlayRequestSources {
    request: PlayRequest
    sources: PlaySource[]
}

export interface PlayServerMedia {
    direct_play_url: string
    can_direct_play: boolean
    hls_url: string
    keep_alive_url: string
    close_session_url: string
    transcode_decision: TranscodeDecision
}
