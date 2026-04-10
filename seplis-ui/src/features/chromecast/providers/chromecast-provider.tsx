import {
    createContext,
    useContext,
    useEffect,
    useRef,
    useState,
    type ReactNode,
} from 'react'
import { useChromecastCafSender } from '../utils/react-chromecast-caf'

interface ChromecastContextValue {
    castState: cast.framework.CastState | null
    sessionState: cast.framework.SessionState | null
    player: cast.framework.RemotePlayer | null
    playerController: cast.framework.RemotePlayerController | null
    isAvailable: boolean
    isConnected: boolean
    requestSession: () => Promise<chrome.cast.ErrorCode | undefined>
    endSession: (stopCasting?: boolean) => void
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

        const onCastStateChange = (e: cast.framework.CastStateEventData) => {
            setCastState(e.castState)
        }
        const onSessionStateChange = (
            e: cast.framework.SessionStateEventData,
        ) => {
            setSessionState(e.sessionState)
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

    const requestSession = () => {
        if (!senderCast)
            return Promise.resolve(undefined as unknown as chrome.cast.ErrorCode)
        return senderCast.framework.CastContext.getInstance().requestSession()
    }

    const endSession = (stopCasting = true) => {
        if (!senderCast) return
        senderCast.framework.CastContext.getInstance().endCurrentSession(
            stopCasting,
        )
    }

    const isConnected =
        castState === senderCast?.framework.CastState.CONNECTED
    const isAvailable =
        castState !== null &&
        castState !== senderCast?.framework.CastState.NO_DEVICES_AVAILABLE

    return (
        <ChromecastContext.Provider
            value={{
                castState,
                sessionState,
                player: playerRef.current,
                playerController: playerControllerRef.current,
                isAvailable,
                isConnected,
                requestSession,
                endSession,
            }}
        >
            {children}
        </ChromecastContext.Provider>
    )
}

export function useChromecast() {
    const ctx = useContext(ChromecastContext)
    if (!ctx)
        throw new Error('useChromecast must be used within a ChromecastProvider')
    return ctx
}
