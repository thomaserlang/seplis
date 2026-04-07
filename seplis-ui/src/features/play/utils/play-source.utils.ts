import { BCP47_TO_ISO6392 } from '../constants/iso6392.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
    PlaySourceStream,
} from '../types/play-source.types'
import { getDefaultMaxBitrate } from './play-bitrate.utils'

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
    defaultMaxBitrate?: number,
) {
    let s: PlayRequestSource = {
        request: playServers[0].request,
        source: playServers[0].sources[0],
    }
    const maxBitrate = defaultMaxBitrate || getDefaultMaxBitrate()
    for (const playServer of playServers.reverse())
        for (const source of playServer.sources)
            if (source.bit_rate <= maxBitrate)
                s = {
                    request: playServer.request,
                    source: source,
                }
    return s
}

function toLangIndex(stream: PlaySourceStream): string {
    return `${stream.language}:${stream.index}`
}

function parseLangIndex(value: string): { lang: string; index: number | null } {
    const parts = value.split(':')
    const index = parts[1] !== undefined ? parseInt(parts[1], 10) : null
    return { lang: parts[0], index: isNaN(index as number) ? null : index }
}

function findByLangIndex(
    streams: PlaySourceStream[],
    langIndex: string,
): PlaySourceStream | undefined {
    const { lang, index } = parseLangIndex(langIndex)
    if (index !== null) {
        const exact = streams.find(
            (s) => s.language === lang && s.index === index,
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
        const match = findByLangIndex(streams, defaultAudio)
        if (match) return toLangIndex(match)
    }
    if (preferredAudioLangs?.length) {
        for (const lang of preferredAudioLangs) {
            const match = streams.find((s) => s.language === lang)
            if (match) return toLangIndex(match)
        }
    }

    return toLangIndex(streams[0])
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
        const match = findByLangIndex(streams, defaultSubtitle)
        return match ? toLangIndex(match) : undefined
    }

    const audioLang = audio ? parseLangIndex(audio).lang : undefined

    // Pick a forced subtitle only if it matches the audio language.
    if (audioLang) {
        const forcedMatch = streams.find(
            (s) => s.forced && s.language === audioLang,
        )
        if (forcedMatch) return toLangIndex(forcedMatch)
    }

    if (preferredSubtitleLangs?.length) {
        for (const lang of preferredSubtitleLangs) {
            const match = streams.find((s) => s.language === lang)
            if (match) {
                // No subtitle needed when the preferred language matches the
                // audio — the user already understands the audio track.
                if (audioLang && match.language === audioLang) return undefined
                return toLangIndex(match)
            }
        }
    }

    return undefined
}
