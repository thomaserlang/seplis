import type { Video as VideoMedia } from '@videojs/core'
import { useMedia } from '@videojs/react'
import { useEffect, type ReactNode } from 'react'
import { PlaySourceStream } from '../types/play-source.types'
import { languageMatch } from '../utils/language-match'

interface PlayerNativeSubtitlesProps {
    subtitle: PlaySourceStream | undefined
    isSafari: boolean
}
export function PlayerNativeSubtitles({
    subtitle,
    isSafari,
}: PlayerNativeSubtitlesProps): ReactNode {
    const media = useMedia() as VideoMedia | null

    useEffect(() => {
        if (!isSafari || !media) return
        const textTracks = media.textTracks
        const applyNativeSubtitleSelection = () => {
            const subtitleTracks = getSubtitleTracks(textTracks)

            if (!subtitle) {
                subtitleTracks.forEach(({ track }) => {
                    track.mode = 'disabled'
                })
                return
            }

            const resolvedTrack = findSubtitleTrack(subtitleTracks, subtitle)

            subtitleTracks.forEach(({ track, index: trackIndex }) => {
                track.mode =
                    resolvedTrack && resolvedTrack.index === trackIndex
                        ? 'showing'
                        : 'disabled'
            })
        }

        applyNativeSubtitleSelection()
    }, [subtitle, isSafari, media])

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
    subtitle: PlaySourceStream,
): IndexedTextTrack | undefined {
    const indexedTrack = subtitleTracks.find(
        (t) => t.index === subtitle.group_index,
    )

    if (
        indexedTrack?.track.language &&
        languageMatch(indexedTrack.track.language, subtitle.language)
    ) {
        return indexedTrack
    }

    return subtitleTracks
        .filter(
            ({ track }) =>
                track.language &&
                languageMatch(track.language, subtitle.language),
        )
        .toSorted((a, b) => {
            return (
                Math.abs(a.index - (subtitle.group_index || 0)) -
                    Math.abs(b.index - (subtitle.group_index || 0)) ||
                a.index - b.index
            )
        })[0]
}
