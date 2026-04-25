import { BCP47_TO_ISO6392 } from '../constants/iso6392.constants'
import {
    PlayRequestSources,
    PlaySource,
    PlaySourceStream,
} from '../types/play-source.types'
import { languageMatch } from './language-match'
import { canPlayMediaType } from './video.utils'

export function iso6392ToDisplayName(iso6392: string): string | undefined {
    if (typeof navigator === 'undefined') return undefined
    const bcp47 = Object.entries(BCP47_TO_ISO6392).find(
        ([, v]) => v === iso6392,
    )?.[0]
    if (!bcp47) return undefined
    try {
        return new Intl.DisplayNames(navigator.languages, {
            type: 'language',
        }).of(bcp47)
    } catch {
        return undefined
    }
}

export function getBrowserPreferredLangs(): string[] {
    const langs = typeof navigator !== 'undefined' ? navigator.languages : []
    const seen = new Set<string>()
    const result: string[] = []
    for (const tag of langs) {
        const primary = tag.split('-')[0].toLowerCase()
        const iso = BCP47_TO_ISO6392[primary]
        if (iso && !seen.has(iso)) {
            seen.add(iso)
            result.push(iso)
        }
    }
    return result
}

export function playSourceStr(source: PlaySource) {
    let s = `${source.resolution} ${source.codec.toUpperCase()}`
    if (source.video_color_range == 'hdr')
        if (source.video_color_range_type == 'dovi') s += ' Dolby Vision'
        else s += ` HDR`
    return s
}

export function pickStartSource(
    playServers: PlayRequestSources[],
    defaultMaxBitrate: number,
) {
    const candidates = playServers.toReversed().flatMap((playServer) =>
        playServer.sources.map((source) => ({
            request: playServer.request,
            source,
        })),
    )

    const bestDirectPlay = candidates.find(
        ({ source }) =>
            source.bitrate <= defaultMaxBitrate &&
            source.media_type != null &&
            canPlayMediaType(source.media_type),
    )
    if (bestDirectPlay) return bestDirectPlay

    const bestWithinBitrate = candidates.find(
        ({ source }) => source.bitrate <= defaultMaxBitrate,
    )
    return (
        bestWithinBitrate ?? {
            request: playServers[0].request,
            source: playServers[0].sources[0],
        }
    )
}

export function toLangKey(stream: PlaySourceStream): string {
    return `${stream.language}:${stream.group_index}`
}

export function parseLangKey(value: string): {
    lang: string
    index: number | null
} {
    const parts = value.split(':')
    const index = parts[1] !== undefined ? parseInt(parts[1], 10) : null
    return { lang: parts[0], index: isNaN(index as number) ? null : index }
}

function findByLangKey(
    streams: PlaySourceStream[],
    langKey: string,
): PlaySourceStream | undefined {
    const { lang, index } = parseLangKey(langKey)
    if (index !== null) {
        const exact = streams.find(
            (s) => s.language === lang && s.group_index === index,
        )
        if (exact) return exact
    }
    return streams.find((s) => s.language === lang)
}

export function pickStartAudio({
    playSource,
    defaultAudio,
    preferredAudioLangs,
}: {
    playSource: PlaySource
    defaultAudio?: string
    preferredAudioLangs?: string[]
}): string | undefined {
    const streams = playSource.audio
    if (!streams?.length) return undefined

    if (defaultAudio) {
        const match = findByLangKey(streams, defaultAudio)
        if (match) return toLangKey(match)
    }
    if (preferredAudioLangs?.length) {
        for (const lang of preferredAudioLangs) {
            const match = streams.find((s) => languageMatch(s.language, lang))
            if (match) return toLangKey(match)
        }
    }

    return toLangKey(streams[0])
}

export function pickStartSubtitle({
    playSource,
    defaultSubtitle,
    preferredSubtitleLangs,
    audio,
}: {
    playSource: PlaySource
    defaultSubtitle?: string
    preferredSubtitleLangs?: string[]
    audio?: string
}): string | undefined {
    const streams = playSource.subtitles
    if (!streams?.length) return undefined

    if (defaultSubtitle) {
        const match = findByLangKey(streams, defaultSubtitle)
        if (match) return toLangKey(match)
    }

    const audioLang = audio ? parseLangKey(audio).lang : undefined

    if (preferredSubtitleLangs?.length) {
        for (const lang of preferredSubtitleLangs) {
            const match = streams.find((s) => languageMatch(s.language, lang))
            if (match) {
                if (
                    !defaultSubtitle &&
                    audioLang &&
                    languageMatch(match.language, audioLang)
                )
                    return undefined
                return toLangKey(match)
            }
        }
    }

    // Pick a forced subtitle only if it matches the audio language.
    if (audioLang) {
        const forcedMatch = streams.find(
            (s) => s.forced && languageMatch(s.language, audioLang),
        )
        if (forcedMatch) return toLangKey(forcedMatch)
    }

    return undefined
}
