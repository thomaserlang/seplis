import { useEffect, useRef, type ReactNode } from 'react'
import { useMedia } from '@videojs/react'
import type { Video as VideoMedia } from '@videojs/core'
import JASSUB from 'jassub'
import type {
    PlayerVideoAssSubtitleProps,
    PlayerVideoSubtitleOffsetProps,
} from './player-video.types'

const robotoMediumFontUrl =
    'https://fonts.gstatic.com/s/roboto/v51/KFOMCnqEu92Fr1ME7kSn66aGLdTylUAMQXC89YmC2DPNWub2bWmT.ttf'
const robotoMediumItalicFontUrl =
    'https://fonts.gstatic.com/s/roboto/v51/KFOKCnqEu92Fr1Mu53ZEC9_Vu3r1gIhOszmOClHrs6ljXfMMLrPQiA8.ttf'

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
            fonts: [robotoMediumFontUrl, robotoMediumItalicFontUrl],
            availableFonts: {
                'Roboto Medium': robotoMediumFontUrl,
                'Roboto Medium Italic': robotoMediumItalicFontUrl,
                'Roboto Italic': robotoMediumItalicFontUrl,
                Roboto: robotoMediumFontUrl,
            },
            defaultFont: 'Roboto Medium',
            queryFonts: 'localandremote',
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
