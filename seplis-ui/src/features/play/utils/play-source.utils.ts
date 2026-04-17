import { BCP47_TO_ISO6392 } from '../constants/iso6392.constants'
import {
    PlayRequestSource,
    PlayRequestSources,
    PlaySource,
    PlaySourceStream,
} from '../types/play-source.types'
import { languageMatch } from './language-match'

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
    let s: PlayRequestSource = {
        request: playServers[0].request,
        source: playServers[0].sources[0],
    }
    for (const playServer of playServers.reverse())
        for (const source of playServer.sources)
            if (source.bit_rate <= defaultMaxBitrate)
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
            const match = streams.find((s) => languageMatch(s.language, lang))
            if (match) return toLangIndex(match)
        }
    }

    return toLangIndex(streams[0])
}

export function audioCodecLabel(
    codec: string | null,
    title?: string,
): string | null {
    if (!codec) return null
    const c = codec.toLowerCase()
    const t = (title ?? '').toLowerCase()
    const hasAtmos = t.includes('atmos')
    const hasDtsX = t.includes('dts:x') || t.includes('dtsx')
    if (c === 'truehd') return hasAtmos ? 'Atmos' : 'TrueHD'
    if (c === 'eac3') return hasAtmos ? 'Atmos' : 'DD+'
    if (c === 'ac3') return 'Dolby Digital'
    if (c === 'dts') return hasDtsX ? 'DTS:X' : 'DTS'
    if (c === 'dca') return 'DTS'
    if (c.includes('dts-hd') || c.includes('dtshd')) return 'DTS-HD MA'
    if (c === 'aac') return 'AAC'
    if (c === 'mp3') return 'MP3'
    if (c === 'flac') return 'FLAC'
    if (c === 'opus') return 'Opus'
    if (c === 'vorbis') return 'Vorbis'
    if (c.startsWith('pcm_')) return 'PCM'
    return null
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
        if (match) return toLangIndex(match)
    }

    const audioLang = audio ? parseLangIndex(audio).lang : undefined

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
                return toLangIndex(match)
            }
        }
    }

    // Pick a forced subtitle only if it matches the audio language.
    if (audioLang) {
        const forcedMatch = streams.find(
            (s) => s.forced && languageMatch(s.language, audioLang),
        )
        if (forcedMatch) return toLangIndex(forcedMatch)
    }

    return undefined
}
