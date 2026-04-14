export function strToBoolUndefined(
    str: string | undefined | null,
): boolean | undefined {
    if (!str) return undefined
    const s = str.toLowerCase()
    if (s === 'true') return true
    if (s === 'false') return false
    return undefined
}

export function strListToNumList(strl: string[] | undefined | null): number[] {
    if (!strl) return []
    return strl
        .flatMap((s) => s.split(',').map((v) => parseInt(v)))
        .filter((v) => !isNaN(v))
}

export function isEmpty<T>(
    value: T | null | undefined,
): value is null | undefined {
    if (value === null || value === undefined) {
        return true
    }

    if (typeof value === 'string' && value.trim() === '') {
        return true
    }

    if (Array.isArray(value)) {
        if (value.length === 0) {
            return true
        }

        if (typeof value[0] === 'string' && value[0].trim() === '') {
            return true
        }
    }

    return false
}
