import { useEffect, useRef, useState } from 'react'
import { initCastContext, onCastSdkReady } from '../cast-sdk'
import {
    CAST_NAMESPACE,
    CastLoadData,
    CastSenderMessage,
} from '../types/cast-messages.types'

export interface CastSenderState {
    isAvailable: boolean
    isConnected: boolean
    deviceName: string | undefined
    currentTime: number
    duration: number
    isPaused: boolean
    isMediaLoaded: boolean
}

export interface CastSenderAPI {
    state: CastSenderState
    requestSession: () => void
    stopCasting: () => void
    loadMedia: (data: CastLoadData) => void
    togglePlayPause: () => void
    seek: (position: number) => void
    sendMessage: (msg: CastSenderMessage) => void
}

export function useCastSender(): CastSenderAPI {
    const [state, setState] = useState<CastSenderState>({
        isAvailable: false,
        isConnected: false,
        deviceName: undefined,
        currentTime: 0,
        duration: 0,
        isPaused: true,
        isMediaLoaded: false,
    })

    const remotePlayerRef = useRef<any>(null)
    const controllerRef = useRef<any>(null)
    const initializedRef = useRef(false)

    useEffect(() => {
        onCastSdkReady(() => {
            if (initializedRef.current) return
            initializedRef.current = true
            initSender()
        })
    }, [])

    const initSender = () => {
        const castFramework = (window as any).cast?.framework
        if (!castFramework) return

        initCastContext()

        const remotePlayer = new castFramework.RemotePlayer()
        const controller = new castFramework.RemotePlayerController(remotePlayer)
        remotePlayerRef.current = remotePlayer
        controllerRef.current = controller

        const { RemotePlayerEventType, CastContextEventType, SessionState } =
            castFramework

        setState((s) => ({ ...s, isAvailable: true }))

        // Session state changes
        castFramework.CastContext.getInstance().addEventListener(
            CastContextEventType.SESSION_STATE_CHANGED,
            (event: any) => {
                const connected =
                    event.sessionState === SessionState.SESSION_STARTED ||
                    event.sessionState === SessionState.SESSION_RESUMED
                const session =
                    castFramework.CastContext.getInstance().getCurrentSession()
                setState((s) => ({
                    ...s,
                    isConnected: connected,
                    deviceName: connected
                        ? session?.getCastDevice()?.friendlyName
                        : undefined,
                    isMediaLoaded: false,
                    currentTime: 0,
                    duration: 0,
                    isPaused: true,
                }))
            },
        )

        // Remote player event bindings
        controller.addEventListener(
            RemotePlayerEventType.CURRENT_TIME_CHANGED,
            (e: any) => setState((s) => ({ ...s, currentTime: e.value ?? 0 })),
        )
        controller.addEventListener(
            RemotePlayerEventType.DURATION_CHANGED,
            (e: any) => setState((s) => ({ ...s, duration: e.value ?? 0 })),
        )
        controller.addEventListener(
            RemotePlayerEventType.IS_PAUSED_CHANGED,
            (e: any) => setState((s) => ({ ...s, isPaused: e.value ?? true })),
        )
        controller.addEventListener(
            RemotePlayerEventType.IS_MEDIA_LOADED_CHANGED,
            (e: any) => setState((s) => ({ ...s, isMediaLoaded: e.value ?? false })),
        )
    }

    const requestSession = () => {
        const context = (window as any).cast?.framework?.CastContext?.getInstance()
        if (!context) return
        context.requestSession().catch(() => {})
    }

    const stopCasting = () => {
        const context = (window as any).cast?.framework?.CastContext?.getInstance()
        context?.getCurrentSession()?.endSession(true)
    }

    const loadMedia = (data: CastLoadData) => {
        const chromeCast = (window as any).chrome?.cast
        const context = (window as any).cast?.framework?.CastContext?.getInstance()
        const session = context?.getCurrentSession()
        if (!session || !chromeCast) return

        const mediaInfo = new chromeCast.media.MediaInfo('seplis-media', 'video/mp4')
        mediaInfo.customData = data
        mediaInfo.duration = undefined

        const request = new chromeCast.media.LoadRequest(mediaInfo)
        request.currentTime = data.startTime
        session.loadMedia(request).catch((e: any) =>
            console.error('Cast loadMedia failed', e),
        )
    }

    const togglePlayPause = () => {
        controllerRef.current?.playOrPause()
    }

    const seek = (position: number) => {
        if (!remotePlayerRef.current || !controllerRef.current) return
        remotePlayerRef.current.currentTime = position
        controllerRef.current.seek()
    }

    const sendMessage = (msg: CastSenderMessage) => {
        const context = (window as any).cast?.framework?.CastContext?.getInstance()
        const session = context?.getCurrentSession()
        session?.sendMessage(CAST_NAMESPACE, msg).catch(() => {})
    }

    return { state, requestSession, stopCasting, loadMedia, togglePlayPause, seek, sendMessage }
}
