import { PlaySourceStream } from './play-source.types'

export interface CastInfo {
    savePositionUrl: string
    watchedUrl: string
}

export interface PlayerProps {
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    onPlayNext?: () => void
    onSavePosition?: (position: number) => void
    onFinished?: () => void
    defaultAudioKey?: string
    onAudioChange?: (audio: PlaySourceStream | undefined) => void
    defaultSubtitleKey?: string
    onSubtitleChange?: (subtitle: PlaySourceStream | undefined) => void
    defaultStartTime?: number
    castInfo?: CastInfo
}
