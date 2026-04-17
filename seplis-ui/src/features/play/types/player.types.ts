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
    defaultAudio?: string
    onAudioChange?: (audio: string | undefined) => void
    defaultSubtitle?: string
    onSubtitleChange?: (subtitle: string | undefined) => void
    defaultStartTime?: number
    castInfo?: CastInfo
}
