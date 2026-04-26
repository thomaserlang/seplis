import type {
    DecisionBlocker,
    PlaybackTransport,
    StreamDecision,
    TranscodeDecision,
} from '../../../types/transcode-decision.types'
import { bitratePretty } from '../../../utils/play-bitrate.utils'
import { effectivePlaybackMethod } from './transcode-decision-label'

export function decisionSummary(
    transcodeDecision: TranscodeDecision,
    playbackTransport?: PlaybackTransport,
): string {
    const method = effectivePlaybackMethod(transcodeDecision, playbackTransport)

    if (method === 'transcode') {
        const videoTranscodes = isStreamTranscode(transcodeDecision.video)
        const audioTranscodes = isStreamTranscode(transcodeDecision.audio)

        if (videoTranscodes && audioTranscodes) {
            return 'Video and audio transcode.'
        }
        if (videoTranscodes) {
            return 'Video transcodes; audio copies.'
        }
        if (audioTranscodes) {
            return 'Audio transcodes; video copies.'
        }
        return 'Transcoded stream selected.'
    }

    if (method === 'direct_play') {
        return 'Source plays as-is.'
    }

    if (
        playbackTransport === 'hls' &&
        transcodeDecision.method === 'direct_play'
    ) {
        return 'Player selected HLS, repackaged without changing codecs.'
    }

    return 'Streams copy into a new container.'
}

export function streamSummary(stream: StreamDecision): string {
    const sourceCodec = formatCodec(stream.source_codec)
    const targetCodec = formatCodec(stream.target_codec)

    if (stream.action === 'copy') {
        return `${sourceCodec}`
    }

    return `${sourceCodec} -> ${targetCodec}`
}

export function transportLabel(
    playbackTransport: PlaybackTransport | undefined,
    transcodeDecision: TranscodeDecision,
): string {
    if (playbackTransport === 'direct_play') return 'Source file'
    if (playbackTransport === 'hls') return 'HLS'

    return transcodeDecision.method === 'direct_play' ? 'Source file' : 'HLS'
}

export function decisionReasons(
    transcodeDecision: TranscodeDecision,
    playbackTransport?: PlaybackTransport,
): string[] {
    const method = effectivePlaybackMethod(transcodeDecision, playbackTransport)
    const reasons: string[] = []

    if (
        playbackTransport === 'hls' &&
        transcodeDecision.method === 'direct_play'
    ) {
        reasons.push('Player selected HLS delivery.')
    }

    if (method === 'direct_play') return reasons

    const streamBlockers = [
        ...(isStreamTranscode(transcodeDecision.video)
            ? transcodeDecision.video.blockers
            : []),
        ...(isStreamTranscode(transcodeDecision.audio)
            ? transcodeDecision.audio.blockers
            : []),
    ]
    const blockers = [
        ...transcodeDecision.direct_play.blockers,
        ...streamBlockers,
    ]

    blockers.forEach((blocker) => {
        const reason = formatBlocker(blocker, transcodeDecision)
        if (reason && !reasons.includes(reason)) reasons.push(reason)
    })

    return reasons
}

function isStreamTranscode(stream: StreamDecision): boolean {
    return stream.action === 'transcode'
}

function formatBlocker(
    blocker: DecisionBlocker,
    transcodeDecision: TranscodeDecision,
): string {
    switch (blocker.code) {
        case 'forced':
            return 'Forced'
        case 'unsupported_codec':
            return formatCodecBlocker(blocker, transcodeDecision)
        case 'unsupported_hdr':
            return `HDR: ${formatDecisionValue(blocker.actual)}`
        case 'limit_exceeded':
            return `${formatLimitKind(blocker.limit_kind)}: ${formatLimitValue(
                blocker.actual,
                blocker.limit_kind,
            )} > ${formatLimitValue(blocker.limit, blocker.limit_kind)}`
        case 'missing_keyframes':
            return 'Missing keyframes'
        case 'video_transcode_requires_audio_transcode':
            return 'Video transcode needs audio transcode'
        case 'unsupported_container':
            return `Container: ${formatDecisionValue(blocker.actual)}`
        case 'audio_track_switch_unsupported':
            return 'Selected audio track requires transcoding.'
        default:
            return formatReason(blocker.code)
    }
}

function formatCodecBlocker(
    blocker: DecisionBlocker,
    transcodeDecision: TranscodeDecision,
): string {
    const stream = streamForBlocker(blocker, transcodeDecision)

    if (!stream) {
        return `${formatScope(blocker)} codec unsupported`
    }

    return `${formatScope(blocker)} codec: ${streamSummary(stream)}`
}

function streamForBlocker(
    blocker: DecisionBlocker,
    transcodeDecision: TranscodeDecision,
): StreamDecision | undefined {
    const streamKind = blocker.stream ?? blocker.scope

    if (streamKind === 'video') return transcodeDecision.video
    if (streamKind === 'audio') return transcodeDecision.audio

    return undefined
}

function formatReason(reason: string): string {
    const formatted = reason.replaceAll('_', ' ').trim()

    if (!formatted) return reason
    return formatted.charAt(0).toUpperCase() + formatted.slice(1)
}

function formatCodec(value: string | null | undefined): string {
    return value?.trim() || 'unknown'
}

function formatScope(blocker: DecisionBlocker): string {
    return formatReason(blocker.stream ?? blocker.scope)
}

function formatLimitKind(limitKind: DecisionBlocker['limit_kind']): string {
    if (!limitKind) return 'Value'

    return formatReason(limitKind)
}

function formatLimitValue(
    value: number | string | null | undefined,
    limitKind?: DecisionBlocker['limit_kind'],
): string {
    if (typeof value === 'number' && limitKind === 'video_bitrate') {
        return bitratePretty(value)
    }

    return formatDecisionValue(value)
}

function formatDecisionValue(
    value: number | string | null | undefined,
): string {
    if (value == null) return 'unknown'
    if (typeof value === 'string') return value.trim() || 'unknown'

    return value.toLocaleString()
}
