export interface IPlayRequest {
    play_id: string
    play_url: string
}


export interface IPlaySourceStream {
    title: string
    language: string
    index: number
    group_index: number | null
    codec: string | null
    forced: boolean
    default: boolean
}


export interface IPlaySource {
    width: number
    height: number
    codec: string
    duration: number
    resolution: string
    audio: IPlaySourceStream[]
    subtitles: IPlaySourceStream[]
    video_color_bit_depth: number
    video_color_range: string
    video_color_range_type: string
    index: number
    size: number
    bit_rate: number
    format: string
}


export interface IPlayServerRequestSource {
    request: IPlayRequest
    source: IPlaySource
}


export interface IPlayServerRequestSources {
    request: IPlayRequest
    sources: IPlaySource[]
}


export interface IPlayServerRequestMedia {
    direct_play_url: string
    can_direct_play: boolean
    hls_url: string
    keep_alive_url: string
    close_session_url: string
}