import { CAST_SESSION_STORAGE_KEY } from '../constants'

export function readStoredCastSession(): boolean {
    try {
        return localStorage.getItem(CAST_SESSION_STORAGE_KEY) === '1'
    } catch {
        return false
    }
}

export function writeStoredCastSession(active: boolean) {
    try {
        if (active) localStorage.setItem(CAST_SESSION_STORAGE_KEY, '1')
        else localStorage.removeItem(CAST_SESSION_STORAGE_KEY)
    } catch {}
}

export function isInactiveSessionState(
    sessionState: cast.framework.SessionState | null,
) {
    return (
        sessionState === null ||
        sessionState === 'NO_SESSION' ||
        sessionState === 'SESSION_ENDING' ||
        sessionState === 'SESSION_ENDED' ||
        sessionState === 'SESSION_START_FAILED'
    )
}

export function isPendingSessionState(
    sessionState: cast.framework.SessionState | null,
) {
    return (
        sessionState === 'SESSION_STARTING' || sessionState === 'SESSION_ENDING'
    )
}

export function getCastSessionObj(
    castSession: cast.framework.CastSession | null,
) {
    try {
        return castSession?.getSessionObj() ?? null
    } catch {
        return null
    }
}
