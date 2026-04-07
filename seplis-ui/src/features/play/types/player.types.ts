export interface PlayerProps {
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    onSavePosition?: (position: number) => void
    onFinished?: () => void
    defaultAudio?: string
    onAudioChange?: (audio: string | undefined) => void
    defaultSubtitle?: string
    onSubtitleChange?: (subtitle: string | undefined) => void
    defaultStartTime?: number
}
