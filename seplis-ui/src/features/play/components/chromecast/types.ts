import type {
    AudioCodec,
    HDRType,
    VideoCodec,
    VideoContainer,
} from '@/features/play/types/media.types'

export interface ChromecastCapabilities {
    supportedVideoCodecs: VideoCodec[]
    supportedAudioCodecs: AudioCodec[]
    supportedVideoContainers: VideoContainer[]
    supportedHdrFormats: HDRType[]
    hdrEnabled: boolean
    maxAudioChannels: number
    maxWidth: number
}

export interface ChromecastCapabilitiesMessage {
    type: 'capabilities'
    payload: ChromecastCapabilities
}

export interface ChromecastCapabilitiesRequestMessage {
    type: 'getCapabilities'
}

export interface ChromecastSubtitleOffsetMessage {
    type: 'subtitleOffset'
    offset: number
}

export interface ChromecastPlaybackError {
    reason?: string
    detailedErrorCode?: number
}

export interface ChromecastPlaybackErrorMessage {
    type: 'playbackError'
    payload: ChromecastPlaybackError | null
}

export type ChromecastMessage =
    | ChromecastCapabilitiesMessage
    | ChromecastCapabilitiesRequestMessage
    | ChromecastSubtitleOffsetMessage
    | ChromecastPlaybackErrorMessage
