import { createContext, useContext, type ReactNode } from 'react'
import type { ChromecastCapabilities, ChromecastPlaybackError } from '../types'

export interface ChromecastContextValue {
    castState: cast.framework.CastState | null
    sessionState: cast.framework.SessionState | null
    castSession: cast.framework.CastSession | null
    mediaSession: chrome.cast.media.Media | null
    player: cast.framework.RemotePlayer | null
    playerController: cast.framework.RemotePlayerController | null
    isAvailable: boolean
    isConnected: boolean
    isConnecting: boolean
    isRecoveringSession: boolean
    capabilities: ChromecastCapabilities | null
    playbackError: ChromecastPlaybackError | null
    loadError: unknown
    requestSession: () => Promise<chrome.cast.ErrorCode | undefined>
    endSession: (stopCasting?: boolean) => Promise<void>
    playPause: () => Promise<void>
    seekMedia: (time: number) => Promise<void>
    loadMedia: (
        request: chrome.cast.media.LoadRequest,
    ) => Promise<chrome.cast.ErrorCode | undefined>
    editTracks: (activeTrackIds: number[]) => Promise<void>
    sendMessage: (namespace: string, message: unknown) => Promise<void>
}

export interface ChromecastProviderProps {
    children: ReactNode
    receiverApplicationId?: string
}

export const ChromecastContext = createContext<ChromecastContextValue | null>(
    null,
)

export function useChromecast() {
    const ctx = useContext(ChromecastContext)
    if (!ctx)
        throw new Error(
            'useChromecast must be used within a ChromecastProvider',
        )
    return ctx
}
