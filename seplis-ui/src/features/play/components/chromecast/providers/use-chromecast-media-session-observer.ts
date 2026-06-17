import { useEffect } from 'react'
import { RESUME_SYNC_DELAYS } from '../constants'
import {
    getCastSessionMediaSession,
    getMediaSessionStatus,
} from '../utils/chromecast-media-session.utils'
import { getCastSessionObj } from '../utils/chromecast-session.utils'

interface Props {
    castSession: cast.framework.CastSession | null
    onMediaSessionChange: (mediaSession: chrome.cast.media.Media | null) => void
}

export function useChromecastMediaSessionObserver({
    castSession,
    onMediaSessionChange,
}: Props) {
    useEffect(() => {
        if (!castSession) {
            onMediaSessionChange(null)
            return
        }

        const sessionObj = getCastSessionObj(castSession)
        let observedMediaSession: chrome.cast.media.Media | null = null

        function updateMediaSession() {
            const nextMediaSession = getCastSessionMediaSession(castSession)
            observeMediaSession(nextMediaSession)
            onMediaSessionChange(nextMediaSession)
        }

        function handleMediaUpdate() {
            if (observedMediaSession) {
                onMediaSessionChange(observedMediaSession)
                return
            }

            updateMediaSession()
        }

        function observeMediaSession(
            nextMediaSession: chrome.cast.media.Media | null,
        ) {
            if (observedMediaSession === nextMediaSession) return

            if (observedMediaSession) {
                try {
                    observedMediaSession.removeUpdateListener(handleMediaUpdate)
                } catch {}
            }

            observedMediaSession = nextMediaSession

            if (observedMediaSession) {
                try {
                    observedMediaSession.addUpdateListener(handleMediaUpdate)
                } catch {}
            }
        }

        function handleSessionMedia(nextMediaSession: chrome.cast.media.Media) {
            observeMediaSession(nextMediaSession)
            onMediaSessionChange(nextMediaSession)
        }

        function refreshMediaSession() {
            const nextMediaSession = getCastSessionMediaSession(castSession)
            if (!nextMediaSession) {
                updateMediaSession()
                return
            }

            getMediaSessionStatus(nextMediaSession)
                .then(updateMediaSession)
                .catch(updateMediaSession)
        }

        updateMediaSession()
        castSession.addEventListener(
            cast.framework.SessionEventType.MEDIA_SESSION,
            updateMediaSession,
        )
        try {
            sessionObj?.addMediaListener(handleSessionMedia)
        } catch {}
        const mediaRefreshTimers = RESUME_SYNC_DELAYS.map((delay) =>
            window.setTimeout(refreshMediaSession, delay),
        )

        return () => {
            for (const timer of mediaRefreshTimers) window.clearTimeout(timer)
            castSession.removeEventListener(
                cast.framework.SessionEventType.MEDIA_SESSION,
                updateMediaSession,
            )
            try {
                sessionObj?.removeMediaListener(handleSessionMedia)
            } catch {}
            observeMediaSession(null)
        }
    }, [castSession, onMediaSessionChange])
}
