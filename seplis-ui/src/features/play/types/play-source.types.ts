export interface PlayRequest {
    play_id: string
    play_url: string
}

export interface PlaySourceStream {
    title: string
    language: string
    index: number
    group_index: number | null
    codec: string | null
    forced: boolean
    default: boolean
}

export interface PlaySource {
    width: number
    height: number
    codec: string
    duration: number
    resolution: string
    audio: PlaySourceStream[]
    subtitles: PlaySourceStream[]
    video_color_bit_depth: number
    video_color_range: string
    video_color_range_type: string
    index: number
    size: number
    bit_rate: number
    format: string
}

export interface PlayRequestSource {
    request: PlayRequest
    source: PlaySource
}

export interface PlayRequestSources {
    request: PlayRequest
    sources: PlaySource[]
}

export interface PlayServerRequestMedia {
    direct_play_url: string
    can_direct_play: boolean
    hls_url: string
    keep_alive_url: string
    close_session_url: string
}
