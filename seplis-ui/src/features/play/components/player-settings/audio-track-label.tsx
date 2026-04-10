import { type ReactNode } from 'react'
import {
    audioCodecLabel,
    iso6392ToDisplayName,
} from '../../utils/play-source.utils'
import classes from './player-settings.module.css'

export function trackLabel(
    title: string | undefined,
    language: string,
): string {
    const base = title || language
    const displayName = iso6392ToDisplayName(language)
    if (!displayName) return base
    if (base === language) return displayName
    if (base.toLowerCase().includes(displayName.toLowerCase())) return base
    return `${base} (${displayName})`
}

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
