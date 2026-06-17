import { getCastSessionObj } from './chromecast-session.utils'

export function getCastSessionMediaSession(
    castSession: cast.framework.CastSession | null,
) {
    if (!castSession) return null

    try {
        return (
            castSession.getMediaSession() ??
            getCastSessionObj(castSession)?.media?.[0] ??
            null
        )
    } catch {
        return null
    }
}

export function stopMediaSession(mediaSession: chrome.cast.media.Media | null) {
    if (!mediaSession) return

    try {
        mediaSession.stop(
            new chrome.cast.media.StopRequest(),
            () => {},
            () => {},
        )
    } catch {}
}

export function runMediaCommand(
    run: (
        success: () => void,
        error: (error: chrome.cast.Error) => void,
    ) => void,
) {
    return new Promise<void>((resolve, reject) => {
        try {
            run(resolve, reject)
        } catch (error) {
            reject(error)
        }
    })
}

export function getMediaSessionStatus(mediaSession: chrome.cast.media.Media) {
    return runMediaCommand((success, error) => {
        mediaSession.getStatus(
            new chrome.cast.media.GetStatusRequest(),
            success,
            error,
        )
    })
}

export function getMediaSessionCurrentTime(
    mediaSession: chrome.cast.media.Media | null,
) {
    if (!mediaSession) return null

    try {
        return mediaSession.getEstimatedTime()
    } catch {
        return mediaSession.currentTime
    }
}

export function getMediaSessionCanSeek(
    mediaSession: chrome.cast.media.Media | null,
) {
    if (!mediaSession) return null

    try {
        return mediaSession.supportsCommand(chrome.cast.media.MediaCommand.SEEK)
    } catch {
        return false
    }
}
