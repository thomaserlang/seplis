import { BCP47_TO_ISO6392 } from '../constants/iso6392.constants'

function toISO6392(lang: string): string {
    const lower = lang.toLowerCase()
    return BCP47_TO_ISO6392[lower] ?? lower
}

export function languageMatch(lang1: string, lang2: string): boolean {
    return toISO6392(lang1) === toISO6392(lang2)
}
