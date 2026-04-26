import type { UsePlaySettings } from '../../hooks/use-play-settings'
import type {
    PlayRequestSource,
    PlayRequestSources,
    PlaySourceStream,
} from '../../types/play-source.types'
import type {
    PlaybackTransport,
    TranscodeDecision,
} from '../../types/transcode-decision.types'

export interface PlayerSettingsProps {
    playRequestSource: PlayRequestSource
    playRequestsSources: PlayRequestSources[]
    audio: PlaySourceStream | undefined
    forceTranscode: boolean
    subtitle: PlaySourceStream | undefined
    subtitleOffset: number
    canAdjustSubtitleOffset: boolean
    onSourceChange: (source: PlayRequestSource) => void
    onAudioChange: (source: PlaySourceStream | undefined) => void
    onForceTranscodeChange: (value: boolean) => void
    onSubtitleChange: (source: PlaySourceStream | undefined) => void
    onSubtitleOffsetChange: (offset: number) => void
    preferredAudioLangs?: string[]
    preferredSubtitleLangs?: string[]
    onClose?: () => void
    playSettings: UsePlaySettings
    transcodeDecision?: TranscodeDecision
    playbackTransport?: PlaybackTransport
}
