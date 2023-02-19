export interface IPlayRequest {
    play_id: string
    play_url: string
}


export interface IPlaySourceStream {
    title: string
    language: string
    index: number
    codec: number | null
}


export interface IPlaySource {
    width: number
    height: number
    codec: string
    duration: number
    audio: IPlaySourceStream[]
    subtitles: IPlaySourceStream[]
    index: number
}


export interface IPlayServerSource {
    request: IPlayRequest
    source: IPlaySource
}


export interface IPlayServerSources {
    request: IPlayRequest
    sources: IPlaySource[]
}
