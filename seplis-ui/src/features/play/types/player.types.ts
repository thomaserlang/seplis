export interface PlayerProps {
    title?: string
    secondaryTitle?: string
    onClose?: () => void
    onSavePosition?: (position: number) => void
    onFinished?: () => void
    defaultAudio?: string
    defaultSubtitle?: string
    defaultStartTime?: number
}
