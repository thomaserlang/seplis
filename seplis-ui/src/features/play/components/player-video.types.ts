import type { CSSProperties } from 'react'
import type { UsePlaySettings } from '../hooks/use-play-settings'
import type {
    PlayRequestSource,
    PlayRequestSources,
} from '../types/play-source.types'

export type PlayErrorType = 'stall_timeout'

export interface PlayErrorEvent {
    type: PlayErrorType
    count: number
}

export interface VideoPlayerProps {
    playRequestSource: PlayRequestSource
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    onPlayNext?: () => void
    playRequestsSources: PlayRequestSources[]
    audioKey: string | undefined
    forceTranscode: boolean
    onSourceChange: (source: PlayRequestSource) => void
    onAudioKeyChange: (audio: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleKeyChange?: (subtitle: string | undefined) => void
    onPlayError?: (event: PlayErrorEvent) => void
    timeSliderStyle?: CSSProperties
    defaultSubtitleKey?: string
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    defaultStartTime?: number
    onVideoReady?: () => void
    onVideoError?: () => void
    onTimeUpdate?: (currentTime: number, duration: number) => void
    playSettings: UsePlaySettings
}

export interface PlayerVideoMediaProps {
    onVideoReady?: () => void
    onVideoError?: () => void
    onTimeUpdate?: (currentTime: number, duration: number) => void
    startTime: number
}

export interface PlayerVideoAssSubtitleProps {
    subUrl: string
    offset: number
}

export interface PlayerVideoSubtitleOffsetProps {
    offset: number
}

export interface PlayerVideoPlayErrorHandlerProps {
    src: string | undefined
    isMediaLoading: boolean
    onPlayError?: (type: PlayErrorType) => void
}

export interface PlayerVideoHlsProps {
    src: string
    startTimeRef: { current: number }
}

export interface PlayerVideoControlsProps {
    onClose?: () => void
    title?: string
    secondaryTitle?: string
    onPlayNext?: () => void
    timeSliderStyle?: CSSProperties
    playRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    audio: string | undefined
    forceTranscode: boolean
    activeSubtitleKey?: string
    subtitleOffset: number
    canAdjustSubtitleOffset: boolean
    onSourceChange: (source: PlayRequestSource) => void
    onAudioChange: (audio: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange: (subtitle: string | undefined) => void
    onSubtitleOffsetChange: (value: number) => void
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    playSettings: UsePlaySettings
}

export interface PlayerVideoStatusProps {
    isPlayerLoading: boolean
    error: unknown
    hasData: boolean
    isLoading: boolean
    onClose?: () => void
}
