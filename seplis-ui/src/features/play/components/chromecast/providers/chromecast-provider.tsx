import {
    createContext,
    useContext,
    useEffect,
    useRef,
    useState,
    type ReactNode,
} from 'react'
import { CAST_NAMESPACE } from '../constants'
import type {
    ChromecastCapabilities,
    ChromecastCapabilitiesMessage,
    ChromecastMessage,
    ChromecastPlaybackError,
    ChromecastPlaybackErrorMessage,
} from '../types'
import { useChromecastCafSender } from '../utils/react-chromecast-caf'

interface ChromecastContextValue {
    castState: cast.framework.CastState | null
    sessionState: cast.framework.SessionState | null
    castSession: cast.framework.CastSession | null
    player: cast.framework.RemotePlayer | null
    playerController: cast.framework.RemotePlayerController | null
    isAvailable: boolean
    isConnected: boolean
    capabilities: ChromecastCapabilities | null
    playbackError: ChromecastPlaybackError | null
    requestSession: () => Promise<chrome.cast.ErrorCode | undefined>
    endSession: (stopCasting?: boolean) => void
    sendMessage: (namespace: string, message: unknown) => Promise<void>
}

const ChromecastContext = createContext<ChromecastContextValue | null>(null)

interface Props {
    children: ReactNode
    receiverApplicationId?: string
}

export function ChromecastProvider({ children, receiverApplicationId }: Props) {
    const { cast: senderCast, chrome: senderChrome } = useChromecastCafSender()
    const [castState, setCastState] = useState<cast.framework.CastState | null>(
        null,
    )
    const [sessionState, setSessionState] =
        useState<cast.framework.SessionState | null>(null)
    const [castSession, setCastSession] =
        useState<cast.framework.CastSession | null>(null)
    const [capabilities, setCapabilities] =
        useState<ChromecastCapabilities | null>(null)
    const [playbackError, setPlaybackError] =
        useState<ChromecastPlaybackError | null>(null)
    const playerRef = useRef<cast.framework.RemotePlayer | null>(null)
    const playerControllerRef =
        useRef<cast.framework.RemotePlayerController | null>(null)
    const [, setPlayerRevision] = useState(0)

    useEffect(() => {
        if (!senderCast || !senderChrome) return

        const castContext = senderCast.framework.CastContext.getInstance()
        castContext.setOptions({
            receiverApplicationId:
                receiverApplicationId ??
                senderChrome.cast.media.DEFAULT_MEDIA_RECEIVER_APP_ID,
            autoJoinPolicy: senderChrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
        })

        const player = new senderCast.framework.RemotePlayer()
        const playerController =
            new senderCast.framework.RemotePlayerController(player)
        playerRef.current = player
        playerControllerRef.current = playerController

        setCastState(castContext.getCastState())
        setSessionState(castContext.getSessionState())
        setCastSession(castContext.getCurrentSession())

        const onCastStateChange = (e: cast.framework.CastStateEventData) => {
            setCastState(e.castState)
        }
        const onSessionStateChange = (
            e: cast.framework.SessionStateEventData,
        ) => {
            setSessionState(e.sessionState)
            setCastSession(castContext.getCurrentSession())
            if (
                e.sessionState ===
                    senderCast.framework.SessionState.SESSION_ENDED ||
                e.sessionState ===
                    senderCast.framework.SessionState.NO_SESSION
            ) {
                setCapabilities(null)
                setPlaybackError(null)
            }
        }
        const onPlayerChange = () => {
            setPlayerRevision((r) => r + 1)
        }

        castContext.addEventListener(
            senderCast.framework.CastContextEventType.CAST_STATE_CHANGED,
            onCastStateChange,
        )
        castContext.addEventListener(
            senderCast.framework.CastContextEventType.SESSION_STATE_CHANGED,
            onSessionStateChange,
        )
        playerController.addEventListener(
            senderCast.framework.RemotePlayerEventType.ANY_CHANGE,
            onPlayerChange,
        )

        return () => {
            castContext.removeEventListener(
                senderCast.framework.CastContextEventType.CAST_STATE_CHANGED,
                onCastStateChange,
            )
            castContext.removeEventListener(
                senderCast.framework.CastContextEventType.SESSION_STATE_CHANGED,
                onSessionStateChange,
            )
            playerController.removeEventListener(
                senderCast.framework.RemotePlayerEventType.ANY_CHANGE,
                onPlayerChange,
            )
            playerRef.current = null
            playerControllerRef.current = null
        }
    }, [senderCast, senderChrome, receiverApplicationId])

    useEffect(() => {
        if (!castSession) {
            setCapabilities(null)
            setPlaybackError(null)
            return
        }

        setCapabilities(null)
        setPlaybackError(null)

        const handleMessage = (
            namespace: string,
            message: ChromecastMessage | string,
        ) => {
            if (namespace !== CAST_NAMESPACE) return

            let data: ChromecastMessage
            try {
                data =
                    typeof message === 'string'
                        ? (JSON.parse(message) as ChromecastMessage)
                        : message
            } catch {
                return
            }

            if (data.type === 'capabilities') {
                setCapabilities(
                    (data as ChromecastCapabilitiesMessage).payload,
                )
            } else if (data.type === 'playbackError') {
                setPlaybackError(
                    (data as ChromecastPlaybackErrorMessage).payload,
                )
            }
        }

        castSession.addMessageListener(CAST_NAMESPACE, handleMessage)
        castSession
            .sendMessage(CAST_NAMESPACE, { type: 'getCapabilities' })
            .catch(() => {})

        return () => {
            castSession.removeMessageListener(CAST_NAMESPACE, handleMessage)
        }
    }, [castSession])

    const requestSession = () => {
        if (!senderCast)
            return Promise.resolve(
                undefined as unknown as chrome.cast.ErrorCode,
            )
        return senderCast.framework.CastContext.getInstance().requestSession()
    }

    const endSession = (stopCasting = true) => {
        if (!senderCast) return
        senderCast.framework.CastContext.getInstance().endCurrentSession(
            stopCasting,
        )
    }

    const sendMessage = async (namespace: string, message: unknown) => {
        if (!senderCast) return
        const session =
            senderCast.framework.CastContext.getInstance().getCurrentSession()
        if (!session) return
        await session.sendMessage(namespace, message)
    }

    const isConnected = castState === senderCast?.framework.CastState.CONNECTED
    const isAvailable =
        castState !== null &&
        castState !== senderCast?.framework.CastState.NO_DEVICES_AVAILABLE

    return (
        <ChromecastContext.Provider
            value={{
                castState,
                sessionState,
                castSession,
                player: playerRef.current,
                playerController: playerControllerRef.current,
                isAvailable,
                isConnected,
                capabilities,
                playbackError,
                requestSession,
                endSession,
                sendMessage,
            }}
        >
            {children}
        </ChromecastContext.Provider>
    )
}

export function useChromecast() {
    const ctx = useContext(ChromecastContext)
    if (!ctx)
        throw new Error(
            'useChromecast must be used within a ChromecastProvider',
        )
    return ctx
}
