import type {
    PlaybackMethod,
    PlaybackTransport,
    TranscodeDecision,
} from '../../../types/transcode-decision.types'

export function transcodeDecisionLabel(
    transcodeDecision: TranscodeDecision | undefined,
    playbackTransport?: PlaybackTransport,
): string {
    if (!transcodeDecision) return 'Unavailable'

    switch (effectivePlaybackMethod(transcodeDecision, playbackTransport)) {
        case 'direct_play':
            return 'Direct Play'
        case 'remux':
            return 'Direct Stream'
        case 'transcode':
            return 'Transcoding'
    }
}

export function effectivePlaybackMethod(
    transcodeDecision: TranscodeDecision,
    playbackTransport?: PlaybackTransport,
): PlaybackMethod {
    if (
        playbackTransport === 'hls' &&
        transcodeDecision.method === 'direct_play'
    ) {
        return 'remux'
    }

    return transcodeDecision.method
}
