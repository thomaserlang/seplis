import type { Video as VideoMedia } from '@videojs/core'
import { useMedia } from '@videojs/react'
import { useEffect, type ReactNode } from 'react'
import { languageMatch } from '../utils/language-match'
import { parseLangKey } from '../utils/play-source.utils'

interface PlayerNativeSubtitlesProps {
    subtitleKey: string | undefined
    isSafari: boolean
}
export function PlayerNativeSubtitles({
    subtitleKey,
    isSafari,
}: PlayerNativeSubtitlesProps): ReactNode {
    const media = useMedia() as VideoMedia | null

    useEffect(() => {
        if (!isSafari || !media) return
        const textTracks = media.textTracks
        const applyNativeSubtitleSelection = () => {
            const subtitleTracks = getSubtitleTracks(textTracks)

            if (!subtitleKey) {
                subtitleTracks.forEach(({ track }) => {
                    track.mode = 'disabled'
                })
                return
            }

            const resolvedTrack = findSubtitleTrack(subtitleTracks, subtitleKey)

            subtitleTracks.forEach(({ track, index: trackIndex }) => {
                track.mode =
                    resolvedTrack && resolvedTrack.index === trackIndex
                        ? 'showing'
                        : 'disabled'
            })
        }

        applyNativeSubtitleSelection()
    }, [subtitleKey, isSafari, media])

    return null
}

type IndexedTextTrack = {
    index: number
    track: SubtitleTextTrack
}

type SubtitleTextTrack = {
    kind: string
    language: string
    mode: string
}

type TextTrackCollection = {
    length: number
    [index: number]: SubtitleTextTrack
}

function getSubtitleTracks(
    textTracks: TextTrackCollection,
): IndexedTextTrack[] {
    return Array.from({ length: textTracks.length })
        .map((_, index) => ({
            index,
            track: textTracks[index],
        }))
        .filter(
            ({ track }) =>
                track.kind === 'subtitles' || track.kind === 'captions',
        )
}

function findSubtitleTrack(
    subtitleTracks: IndexedTextTrack[],
    subtitleKey: string,
): IndexedTextTrack | undefined {
    const { lang, index } = parseLangKey(subtitleKey)
    const indexedTrack =
        index !== null
            ? subtitleTracks.find((t) => t.index === index)
            : undefined

    if (
        indexedTrack?.track.language &&
        languageMatch(indexedTrack.track.language, lang)
    ) {
        return indexedTrack
    }

    return subtitleTracks
        .filter(
            ({ track }) =>
                track.language && languageMatch(track.language, lang),
        )
        .toSorted((a, b) => {
            if (index === null) return a.index - b.index
            return (
                Math.abs(a.index - index) - Math.abs(b.index - index) ||
                a.index - b.index
            )
        })[0]
}
