export interface IPlayRequest {
    play_id: string
    play_url: string
}


export interface IPlaySourceStream {
    title: string
    language: string
    index: number
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
}


export interface IPlayServerRequestSource {
    request: IPlayRequest
    source: IPlaySource
}


export interface IPlayServerRequestSources {
    request: IPlayRequest
    sources: IPlaySource[]
}
