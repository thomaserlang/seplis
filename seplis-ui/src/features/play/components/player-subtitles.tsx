import { useEffect, useRef, type ReactNode } from 'react'
import { useMedia } from '@videojs/react'
import type { Video as VideoMedia } from '@videojs/core'
import JASSUB from 'jassub'
import type {
    PlayerVideoAssSubtitleProps,
    PlayerVideoSubtitleOffsetProps,
} from './player-video.types'

export function AssSubtitle({
    subUrl,
    offset,
}: PlayerVideoAssSubtitleProps): ReactNode {
    const media = useMedia() as VideoMedia | null
    const jassubRef = useRef<JASSUB | null>(null)

    useEffect(() => {
        if (!media) return
        const jassub = new JASSUB({
            video: media as unknown as HTMLVideoElement,
            subUrl,
        })
        jassubRef.current = jassub
        return () => {
            jassub.destroy()
            jassubRef.current = null
        }
    }, [media, subUrl])

    useEffect(() => {
        if (jassubRef.current) jassubRef.current.timeOffset = offset
    }, [offset])

    return null
}

export function SubtitleOffsetApplier({
    offset,
}: PlayerVideoSubtitleOffsetProps): ReactNode {
    const media = useMedia() as VideoMedia | null

    useEffect(() => {
        if (!media) return
        const tracks = media.textTracks
        for (let i = 0; i < tracks.length; i++) {
            const track = tracks[i]
            if (track.kind !== 'subtitles' || !track.cues) continue
            for (const cue of track.cues) {
                if (!('_originalStart' in cue)) {
                    ;(cue as any)._originalStart = cue.startTime
                    ;(cue as any)._originalEnd = cue.endTime
                }
                ;(cue as any).startTime = (cue as any)._originalStart + offset
                ;(cue as any).endTime = (cue as any)._originalEnd + offset
            }
        }
    }, [media, offset])

    return null
}
