import { type ReactNode } from 'react'
import { PlaySourceStream } from '../../types/play-source.types'
import { audioCodecLabel } from '../../utils/play-codec.utils'
import { trackLabel } from '../../utils/play-track.utils'
import classes from './player-settings.module.css'

export function AudioLabel({
    source,
}: {
    source: PlaySourceStream
}): ReactNode {
    const label = trackLabel(source.title, source.language)
    const codec = source.codec ? audioCodecLabel(source.codec) : undefined
    return (
        <span className={classes.audioTrack}>
            {label}
            {codec && <span className={classes.audioCodec}>{codec}</span>}
        </span>
    )
}
