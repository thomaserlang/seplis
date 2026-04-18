import { useEffect, useEffectEvent, useRef } from 'react'
import { useMedia } from '@videojs/react'
import type { Video as VideoMedia } from '@videojs/core'
import type {
    PlayerVideoPlayErrorHandlerProps,
    PlayErrorType,
} from './player-video.types'

const STALL_TIMEOUT = 3_000
const STARTUP_TIMEOUT = 8_000

function getBufferEnd(media: VideoMedia): number {
    if (media.buffered.length === 0) return 0
    return media.buffered.end(media.buffered.length - 1)
}

export function PlayErrorHandler({
    src,
    isMediaLoading,
    onPlayError,
}: PlayerVideoPlayErrorHandlerProps): null {
    const media = useMedia() as VideoMedia | null
    const hasStartedPlaybackRef = useRef(false)
    const sourceLoadStartedAtRef = useRef(0)
    const lastCurrentTimeRef = useRef(0)
    const lastPlaybackProgressAtRef = useRef(0)
    const lastProgressAtRef = useRef(0)
    const lastBufferEndRef = useRef(0)
    const stallReportedRef = useRef(false)

    const fireError = useEffectEvent((type: PlayErrorType) => {
        onPlayError?.(type)
    })

    useEffect(() => {
        hasStartedPlaybackRef.current = false
        sourceLoadStartedAtRef.current = performance.now()
        lastCurrentTimeRef.current = 0
        lastPlaybackProgressAtRef.current = sourceLoadStartedAtRef.current
        lastProgressAtRef.current = sourceLoadStartedAtRef.current
        lastBufferEndRef.current = 0
        stallReportedRef.current = false
    }, [src])

    useEffect(() => {
        if (!isMediaLoading) return
        hasStartedPlaybackRef.current = false
        stallReportedRef.current = false
    }, [isMediaLoading, src])

    useEffect(() => {
        if (!media) return

        const markPlaybackProgress = () => {
            lastCurrentTimeRef.current = media.currentTime
            lastPlaybackProgressAtRef.current = performance.now()
            stallReportedRef.current = false
        }
        const markNetworkProgress = () => {
            lastProgressAtRef.current = performance.now()
            lastBufferEndRef.current = getBufferEnd(media)
            stallReportedRef.current = false
        }
        const handleLoadProgress = () => {
            lastProgressAtRef.current = performance.now()
            stallReportedRef.current = false
        }
        const shouldSkipStallCheck = () =>
            isMediaLoading ||
            media.seeking ||
            media.ended ||
            (hasStartedPlaybackRef.current && media.paused)
        const markPlaybackStarted = () => {
            hasStartedPlaybackRef.current = true
            markPlaybackProgress()
            markNetworkProgress()
        }
        const handleTimeUpdate = () => {
            if (!hasStartedPlaybackRef.current) return
            if (media.currentTime > lastCurrentTimeRef.current + 0.01) {
                markPlaybackProgress()
            }
        }
        const handleSeeking = () => {
            lastCurrentTimeRef.current = media.currentTime
            lastPlaybackProgressAtRef.current = performance.now()
            stallReportedRef.current = false
        }
        const handlePause = () => {
            stallReportedRef.current = false
        }
        const intervalId = window.setInterval(() => {
            if (shouldSkipStallCheck()) return

            const now = performance.now()
            const bufferEnd = getBufferEnd(media)

            if (media.currentTime > lastCurrentTimeRef.current + 0.01) {
                markPlaybackProgress()
                return
            }

            if (bufferEnd > lastBufferEndRef.current + 0.01) {
                markNetworkProgress()
                return
            }

            if (!hasStartedPlaybackRef.current) {
                if (
                    now - sourceLoadStartedAtRef.current < STARTUP_TIMEOUT ||
                    now - lastProgressAtRef.current < STALL_TIMEOUT
                ) {
                    return
                }

                if (!stallReportedRef.current) {
                    stallReportedRef.current = true
                    fireError('stall_timeout')
                }
                return
            }

            if (now - lastProgressAtRef.current < STALL_TIMEOUT) {
                return
            }

            if (now - lastPlaybackProgressAtRef.current < STALL_TIMEOUT) {
                return
            }

            if (!stallReportedRef.current) {
                stallReportedRef.current = true
                fireError('stall_timeout')
            }
        }, 250)

        media.addEventListener('playing', markPlaybackStarted)
        media.addEventListener('timeupdate', handleTimeUpdate)
        media.addEventListener('progress', markNetworkProgress)
        media.addEventListener('loadstart', handleLoadProgress)
        media.addEventListener('loadedmetadata', handleLoadProgress)
        media.addEventListener('loadeddata', handleLoadProgress)
        media.addEventListener('canplay', handleLoadProgress)
        media.addEventListener('canplaythrough', handleLoadProgress)
        media.addEventListener('seeking', handleSeeking)
        media.addEventListener('pause', handlePause)

        return () => {
            window.clearInterval(intervalId)
            media.removeEventListener('playing', markPlaybackStarted)
            media.removeEventListener('timeupdate', handleTimeUpdate)
            media.removeEventListener('progress', markNetworkProgress)
            media.removeEventListener('loadstart', handleLoadProgress)
            media.removeEventListener('loadedmetadata', handleLoadProgress)
            media.removeEventListener('loadeddata', handleLoadProgress)
            media.removeEventListener('canplay', handleLoadProgress)
            media.removeEventListener('canplaythrough', handleLoadProgress)
            media.removeEventListener('seeking', handleSeeking)
            media.removeEventListener('pause', handlePause)
        }
    }, [fireError, isMediaLoading, media])

    return null
}
