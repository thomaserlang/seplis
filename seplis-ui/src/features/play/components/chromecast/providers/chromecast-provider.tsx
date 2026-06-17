import { useCallback, useEffect, useRef, useState } from 'react'
import { RESUME_SYNC_DELAYS } from '../constants'
import type { ChromecastCapabilities, ChromecastPlaybackError } from '../types'
import {
    getCastSessionMediaSession,
    runMediaCommand,
    stopMediaSession,
} from '../utils/chromecast-media-session.utils'
import {
    getCastSessionObj,
    isInactiveSessionState,
    isPendingSessionState,
    readStoredCastSession,
    writeStoredCastSession,
} from '../utils/chromecast-session.utils'
import { useChromecastCafSender } from '../utils/react-chromecast-caf'
import {
    ChromecastContext,
    type ChromecastProviderProps,
} from './chromecast-context'
import { useChromecastMediaSessionObserver } from './use-chromecast-media-session-observer'
import { useChromecastReceiverMessages } from './use-chromecast-receiver-messages'

export function ChromecastProvider({
    children,
    receiverApplicationId,
}: ChromecastProviderProps) {
    const sender = useChromecastCafSender()
    const [castState, setCastState] = useState<cast.framework.CastState | null>(
        null,
    )
    const [sessionState, setSessionState] =
        useState<cast.framework.SessionState | null>(null)
    const [castSession, setCastSession] =
        useState<cast.framework.CastSession | null>(null)
    const [mediaSession, setMediaSession] =
        useState<chrome.cast.media.Media | null>(null)
    const [capabilities, setCapabilities] =
        useState<ChromecastCapabilities | null>(null)
    const [playbackError, setPlaybackError] =
        useState<ChromecastPlaybackError | null>(null)
    const [loadError, setLoadError] = useState<unknown>(null)
    const [isRecoveringSession, setIsRecoveringSession] = useState(
        readStoredCastSession,
    )
    const [isRequestingSession, setIsRequestingSession] = useState(false)
    const [, setPlayerRevision] = useState(0)

    const castContextRef = useRef<cast.framework.CastContext | null>(null)
    const castSessionRef = useRef<cast.framework.CastSession | null>(null)
    const mediaSessionRef = useRef<chrome.cast.media.Media | null>(null)
    const playerRef = useRef<cast.framework.RemotePlayer | null>(null)
    const playerControllerRef =
        useRef<cast.framework.RemotePlayerController | null>(null)

    const setCurrentMediaSession = useCallback(
        (nextMediaSession: chrome.cast.media.Media | null) => {
            mediaSessionRef.current = nextMediaSession
            setMediaSession(nextMediaSession)
            setPlayerRevision((revision) => revision + 1)
        },
        [],
    )

    const clearReceiverState = useCallback(() => {
        castSessionRef.current = null
        mediaSessionRef.current = null
        setCastSession(null)
        setMediaSession(null)
        setCapabilities(null)
        setPlaybackError(null)
        setLoadError(null)
        setIsRecoveringSession(false)
        setIsRequestingSession(false)
        writeStoredCastSession(false)
    }, [])

    const getActiveMediaSession = useCallback(() => {
        const session =
            castSessionRef.current ??
            castContextRef.current?.getCurrentSession() ??
            null
        const nextMediaSession =
            getCastSessionMediaSession(session) ?? mediaSessionRef.current

        if (nextMediaSession !== mediaSessionRef.current) {
            setCurrentMediaSession(nextMediaSession)
        }

        return nextMediaSession
    }, [setCurrentMediaSession])

    const syncFromCastContext = useCallback(() => {
        const castContext = castContextRef.current
        if (!castContext) return null

        const nextCastState = castContext.getCastState()
        const nextSessionState = castContext.getSessionState()
        const nextSession = castContext.getCurrentSession()
        const nextMediaSession = getCastSessionMediaSession(nextSession)

        castSessionRef.current = nextSession

        setCastState(nextCastState)
        setSessionState(nextSessionState)
        setCastSession(nextSession)
        setCurrentMediaSession(nextMediaSession)

        if (nextSession) {
            setIsRecoveringSession(false)
            writeStoredCastSession(true)
            return nextSession
        }

        if (isInactiveSessionState(nextSessionState)) {
            clearReceiverState()
        }

        return null
    }, [clearReceiverState, setCurrentMediaSession])

    useEffect(() => {
        if (sender.status === 'loading') return

        if (sender.status !== 'ready') {
            setCastState(null)
            setSessionState(null)
            clearReceiverState()
            return
        }

        const castContext = sender.cast.framework.CastContext.getInstance()
        castContextRef.current = castContext

        const player = new sender.cast.framework.RemotePlayer()
        const playerController =
            new sender.cast.framework.RemotePlayerController(player)
        playerRef.current = player
        playerControllerRef.current = playerController

        const onCastStateChange = (
            event: cast.framework.CastStateEventData,
        ) => {
            setCastState(event.castState)
            queueMicrotask(syncFromCastContext)
        }

        const onSessionStateChange = (
            event: cast.framework.SessionStateEventData,
        ) => {
            setSessionState(event.sessionState)
            queueMicrotask(syncFromCastContext)

            if (isInactiveSessionState(event.sessionState)) {
                clearReceiverState()
            }
        }

        const onPlayerChange = () => {
            const nextMediaSession = getCastSessionMediaSession(
                castSessionRef.current,
            )
            setCurrentMediaSession(nextMediaSession)
        }

        castContext.addEventListener(
            sender.cast.framework.CastContextEventType.CAST_STATE_CHANGED,
            onCastStateChange,
        )
        castContext.addEventListener(
            sender.cast.framework.CastContextEventType.SESSION_STATE_CHANGED,
            onSessionStateChange,
        )
        playerController.addEventListener(
            sender.cast.framework.RemotePlayerEventType.ANY_CHANGE,
            onPlayerChange,
        )

        castContext.setOptions({
            receiverApplicationId:
                receiverApplicationId ??
                sender.chrome.cast.media.DEFAULT_MEDIA_RECEIVER_APP_ID,
            autoJoinPolicy: sender.chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
            resumeSavedSession: true,
        })
        syncFromCastContext()

        const resumeTimers = RESUME_SYNC_DELAYS.map((delay) =>
            window.setTimeout(syncFromCastContext, delay),
        )

        return () => {
            for (const timer of resumeTimers) window.clearTimeout(timer)
            castContext.removeEventListener(
                sender.cast.framework.CastContextEventType.CAST_STATE_CHANGED,
                onCastStateChange,
            )
            castContext.removeEventListener(
                sender.cast.framework.CastContextEventType
                    .SESSION_STATE_CHANGED,
                onSessionStateChange,
            )
            playerController.removeEventListener(
                sender.cast.framework.RemotePlayerEventType.ANY_CHANGE,
                onPlayerChange,
            )
            castContextRef.current = null
            castSessionRef.current = null
            mediaSessionRef.current = null
            playerRef.current = null
            playerControllerRef.current = null
        }
    }, [
        clearReceiverState,
        receiverApplicationId,
        sender,
        setCurrentMediaSession,
        syncFromCastContext,
    ])

    useEffect(() => {
        castSessionRef.current = castSession

        if (!castSession) {
            setCurrentMediaSession(null)
            setCapabilities(null)
            setPlaybackError(null)
        }
    }, [castSession, setCurrentMediaSession])

    const resetReceiverSessionState = useCallback(() => {
        setCapabilities(null)
        setPlaybackError(null)
        setLoadError(null)
    }, [])

    useChromecastMediaSessionObserver({
        castSession,
        onMediaSessionChange: setCurrentMediaSession,
    })
    useChromecastReceiverMessages({
        castSession,
        onCapabilities: setCapabilities,
        onPlaybackError: setPlaybackError,
        onReset: resetReceiverSessionState,
    })

    const requestSession = useCallback(async () => {
        if (sender.status !== 'ready') return undefined

        const castContext =
            castContextRef.current ??
            sender.cast.framework.CastContext.getInstance()
        castContextRef.current = castContext

        try {
            setIsRequestingSession(true)
            const result = await castContext.requestSession()
            syncFromCastContext()
            return result
        } catch (error) {
            syncFromCastContext()
            return error as chrome.cast.ErrorCode
        } finally {
            setIsRequestingSession(false)
        }
    }, [sender, syncFromCastContext])

    const endSession = useCallback(
        async (stopCasting = true) => {
            if (sender.status !== 'ready') return

            const castContext =
                castContextRef.current ??
                sender.cast.framework.CastContext.getInstance()
            const session =
                castSessionRef.current ?? castContext.getCurrentSession()
            const sessionObj = getCastSessionObj(session)
            const currentMediaSession = getActiveMediaSession()

            try {
                if (session) session.endSession(stopCasting)
                else castContext.endCurrentSession(stopCasting)
            } catch {}

            try {
                castContext.endCurrentSession(stopCasting)
            } catch {}

            try {
                if (stopCasting) {
                    sessionObj?.stop(
                        () => {},
                        () => {},
                    )
                } else {
                    sessionObj?.leave(
                        () => {},
                        () => {},
                    )
                }
            } catch {}

            if (stopCasting) {
                stopMediaSession(currentMediaSession)
            }

            clearReceiverState()
            setCastState(castContext.getCastState())
            setSessionState(castContext.getSessionState())
            window.setTimeout(syncFromCastContext, 500)
        },
        [
            clearReceiverState,
            getActiveMediaSession,
            sender,
            syncFromCastContext,
        ],
    )

    const playPause = useCallback(async () => {
        const currentMediaSession = getActiveMediaSession()

        if (!currentMediaSession) {
            playerControllerRef.current?.playOrPause()
            return
        }

        const shouldPlay =
            currentMediaSession.playerState ===
                chrome.cast.media.PlayerState.PAUSED ||
            currentMediaSession.playerState ===
                chrome.cast.media.PlayerState.IDLE

        if (shouldPlay) {
            await runMediaCommand((success, error) => {
                currentMediaSession.play(
                    new chrome.cast.media.PlayRequest(),
                    success,
                    error,
                )
            })
        } else {
            await runMediaCommand((success, error) => {
                currentMediaSession.pause(
                    new chrome.cast.media.PauseRequest(),
                    success,
                    error,
                )
            })
        }

        setCurrentMediaSession(currentMediaSession)
    }, [getActiveMediaSession, setCurrentMediaSession])

    const seekMedia = useCallback(
        async (time: number) => {
            const currentMediaSession = getActiveMediaSession()

            if (!currentMediaSession) {
                const player = playerRef.current
                if (!player) return

                player.currentTime = time
                playerControllerRef.current?.seek()
                return
            }

            const request = new chrome.cast.media.SeekRequest()
            request.currentTime = time
            request.resumeState =
                currentMediaSession.playerState ===
                chrome.cast.media.PlayerState.PAUSED
                    ? chrome.cast.media.ResumeState.PLAYBACK_PAUSE
                    : chrome.cast.media.ResumeState.PLAYBACK_START

            await runMediaCommand((success, error) => {
                currentMediaSession.seek(request, success, error)
            })

            setCurrentMediaSession(currentMediaSession)
        },
        [getActiveMediaSession, setCurrentMediaSession],
    )

    const loadMedia = useCallback(
        async (request: chrome.cast.media.LoadRequest) => {
            const session =
                castSessionRef.current ??
                castContextRef.current?.getCurrentSession()

            if (!session) {
                const error = new Error('No active Chromecast session')
                setLoadError(error)
                throw error
            }

            try {
                setLoadError(null)
                const result = await session.loadMedia(request)
                const nextMediaSession = getCastSessionMediaSession(session)
                setCurrentMediaSession(nextMediaSession)
                return result
            } catch (error) {
                setLoadError(error)
                throw error
            }
        },
        [setCurrentMediaSession],
    )

    const editTracks = useCallback(
        (activeTrackIds: number[]) => {
            const currentMediaSession = getActiveMediaSession()

            if (!currentMediaSession) return Promise.resolve()

            const request = new chrome.cast.media.EditTracksInfoRequest(
                activeTrackIds,
            )

            return new Promise<void>((resolve, reject) => {
                currentMediaSession.editTracksInfo(
                    request,
                    () => resolve(),
                    (error) => reject(error),
                )
            })
        },
        [getActiveMediaSession],
    )

    const sendMessage = useCallback(
        async (namespace: string, message: unknown) => {
            const session =
                castSessionRef.current ??
                castContextRef.current?.getCurrentSession()

            if (!session) return
            await session.sendMessage(namespace, message)
        },
        [],
    )

    const isReady = sender.status === 'ready'
    const isConnected =
        castSession != null && !isInactiveSessionState(sessionState)
    const isConnecting =
        isRequestingSession ||
        isRecoveringSession ||
        isPendingSessionState(sessionState) ||
        castState === sender.cast?.framework.CastState.CONNECTING
    const isAvailable =
        isReady &&
        castState !== null &&
        castState !== sender.cast.framework.CastState.NO_DEVICES_AVAILABLE

    return (
        <ChromecastContext.Provider
            value={{
                castState,
                sessionState,
                castSession,
                mediaSession,
                player: playerRef.current,
                playerController: playerControllerRef.current,
                isAvailable,
                isConnected,
                isConnecting,
                isRecoveringSession,
                capabilities,
                playbackError,
                loadError,
                requestSession,
                endSession,
                playPause,
                seekMedia,
                loadMedia,
                editTracks,
                sendMessage,
            }}
        >
            {children}
        </ChromecastContext.Provider>
    )
}

export { useChromecast } from './chromecast-context'
