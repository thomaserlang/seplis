import { UsePlaySettings } from '../../hooks/use-play-settings'
import {
    PlayRequestSource,
    PlayRequestSources,
} from '../../types/play-source.types'

export interface PlayerSettingsProps {
    playRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    maxBitrate: number
    audioLang: string | undefined
    forceTranscode: boolean
    activeSubtitleKey: string | undefined
    subtitleOffset: number
    onSourceChange: (source: PlayRequestSource) => void
    onBitrateChange: (bitrate: number) => void
    onAudioLangChange: (lang: string | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange: (key: string | undefined) => void
    onSubtitleOffsetChange: (offset: number) => void
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    onClose?: () => void
    playSettings: UsePlaySettings
}
