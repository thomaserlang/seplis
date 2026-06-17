import { useEffect } from 'react'
import { CAPABILITIES_REQUEST_DELAYS, CAST_NAMESPACE } from '../constants'
import type {
    ChromecastCapabilities,
    ChromecastCapabilitiesMessage,
    ChromecastMessage,
    ChromecastPlaybackError,
    ChromecastPlaybackErrorMessage,
} from '../types'
import { parseChromecastMessage } from '../utils/chromecast-message.utils'

interface Props {
    castSession: cast.framework.CastSession | null
    onCapabilities: (capabilities: ChromecastCapabilities | null) => void
    onPlaybackError: (error: ChromecastPlaybackError | null) => void
    onReset: () => void
}

export function useChromecastReceiverMessages({
    castSession,
    onCapabilities,
    onPlaybackError,
    onReset,
}: Props) {
    useEffect(() => {
        if (!castSession) {
            onCapabilities(null)
            onPlaybackError(null)
            return
        }

        const handleMessage = (
            namespace: string,
            message: ChromecastMessage | string,
        ) => {
            if (namespace !== CAST_NAMESPACE) return

            const data = parseChromecastMessage(message)
            if (!data) return

            if (data.type === 'capabilities') {
                onCapabilities((data as ChromecastCapabilitiesMessage).payload)
            } else if (data.type === 'playbackError') {
                onPlaybackError(
                    (data as ChromecastPlaybackErrorMessage).payload,
                )
            }
        }

        const requestCapabilities = () => {
            castSession
                .sendMessage(CAST_NAMESPACE, { type: 'getCapabilities' })
                .catch(() => {})
        }

        onReset()
        castSession.addMessageListener(CAST_NAMESPACE, handleMessage)
        const capabilityTimers = CAPABILITIES_REQUEST_DELAYS.map((delay) =>
            window.setTimeout(requestCapabilities, delay),
        )

        return () => {
            for (const timer of capabilityTimers) window.clearTimeout(timer)
            castSession.removeMessageListener(CAST_NAMESPACE, handleMessage)
        }
    }, [castSession, onCapabilities, onPlaybackError, onReset])
}
