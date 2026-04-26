export type PlaybackMethod = 'direct_play' | 'remux' | 'transcode'

export type PlaybackTransport = 'direct_play' | 'hls'

export type DecisionScope = 'playback' | 'video' | 'audio' | 'container'

export type StreamKind = 'video' | 'audio'

export type StreamAction = 'copy' | 'transcode'

export type LimitKind =
    | 'audio_channels'
    | 'video_bitrate'
    | 'width'
    | 'video_bit_depth'

export type BlockerCode =
    | 'forced'
    | 'unsupported_codec'
    | 'unsupported_hdr'
    | 'limit_exceeded'
    | 'missing_keyframes'
    | 'video_transcode_requires_audio_transcode'
    | 'unsupported_container'
    | 'audio_track_switch_unsupported'

export interface DecisionBlocker {
    code: BlockerCode
    scope: DecisionScope
    stream?: StreamKind | null
    limit_kind?: LimitKind | null
    limit?: number | null
    actual?: number | string | null
}

export interface DirectPlayDecision {
    supported: boolean
    blockers: DecisionBlocker[]
}

export interface StreamDecision {
    kind: StreamKind
    action: StreamAction
    source_codec: string
    target_codec: string
    blockers: DecisionBlocker[]
}

export interface TranscodeDecision {
    session: string
    method: PlaybackMethod
    required: boolean
    direct_play: DirectPlayDecision
    video: StreamDecision
    audio: StreamDecision
}
