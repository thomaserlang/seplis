import { type ReactNode } from 'react'
import { audioCodecLabel } from '../../utils/play-source.utils'
import { trackLabel } from '../../utils/play-track.utils'
import classes from './player-settings.module.css'

export function AudioTrackLabel({
    track,
}: {
    track: { title: string; language: string; codec: string | null }
}): ReactNode {
    const label = trackLabel(track.title, track.language)
    const codec = audioCodecLabel(track.codec, track.title)
    return (
        <span className={classes.audioTrack}>
            {label}
            {codec && <span className={classes.audioCodec}>{codec}</span>}
        </span>
    )
}
