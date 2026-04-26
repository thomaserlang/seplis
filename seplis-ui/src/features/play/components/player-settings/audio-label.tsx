import { type ReactNode } from 'react'
import { AUDIO_CODEC_LABELS } from '../../constants/media.constants'
import type { AudioCodec } from '../../types/media.types'
import { PlaySourceStream } from '../../types/play-source.types'
import { trackLabel } from '../../utils/play-track.utils'
import classes from './player-settings.module.css'

export function AudioLabel({
    source,
}: {
    source: PlaySourceStream
}): ReactNode {
    const label = trackLabel(source.title, source.language)
    const codec =
        AUDIO_CODEC_LABELS?.[(source.codec as unknown as AudioCodec) ?? ''] ??
        source.codec
    return (
        <span className={classes.audioTrack}>
            {label}
            {codec && <span className={classes.audioCodec}>{codec}</span>}
        </span>
    )
}
