import { iso6392ToDisplayName } from './play-source.utils'

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
