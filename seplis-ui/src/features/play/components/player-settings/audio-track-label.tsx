import { type ReactNode } from 'react'
import { AUDIO_CODEC_LABELS, AudioCodec } from '../../types/media.types'
import { trackLabel } from '../../utils/play-track.utils'
import classes from './player-settings.module.css'

export function AudioTrackLabel({
    track,
}: {
    track: { title: string; language: string; codec: string | null }
}): ReactNode {
    const label = trackLabel(track.title, track.language)
    const codec =
        AUDIO_CODEC_LABELS?.[(track.codec as unknown as AudioCodec) ?? ''] ??
        track.codec
    return (
        <span className={classes.audioTrack}>
            {label}
            {codec && <span className={classes.audioCodec}>{codec}</span>}
        </span>
    )
}
