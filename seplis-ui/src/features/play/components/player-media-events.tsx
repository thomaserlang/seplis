import { useEffect, useRef } from 'react'
import { useMedia } from '@videojs/react'
import type { Video as VideoMedia } from '@videojs/core'
import type { PlayerVideoMediaProps } from './player-video.types'

export function MediaEventHandler({
    onVideoReady,
    onVideoError,
    onTimeUpdate,
    startTime,
}: PlayerVideoMediaProps): null {
    const media = useMedia() as VideoMedia | null
    const resumeTimeRef = useRef<number>(startTime)
    resumeTimeRef.current = startTime

    useEffect(() => {
        if (!media) return

        const handleCanPlay = () => onVideoReady?.()
        const handleError = () => onVideoError?.()
        const handleTimeUpdate = () => {
            if (!media.duration) return
            onTimeUpdate?.(media.currentTime, media.duration)
        }
        const handleVolumeChange = () => {
            localStorage.setItem(
                'player-volume',
                String(Math.round(media.volume * 100) / 100),
            )
        }
        const handleMetadataLoaded = () => {
            media.currentTime = resumeTimeRef.current
        }
        const handleSeeked = () => {
            if (media.paused) media.play().catch(() => {})
        }

        const savedVolume = localStorage.getItem('player-volume')
        media.volume = savedVolume !== null ? parseFloat(savedVolume) : 0.5

        media.addEventListener('canplay', handleCanPlay)
        media.addEventListener('error', handleError)
        media.addEventListener('timeupdate', handleTimeUpdate)
        media.addEventListener('volumechange', handleVolumeChange)
        media.addEventListener('loadedmetadata', handleMetadataLoaded)
        media.addEventListener('seeked', handleSeeked)

        return () => {
            media.removeEventListener('canplay', handleCanPlay)
            media.removeEventListener('error', handleError)
            media.removeEventListener('timeupdate', handleTimeUpdate)
            media.removeEventListener('volumechange', handleVolumeChange)
            media.removeEventListener('loadedmetadata', handleMetadataLoaded)
            media.removeEventListener('seeked', handleSeeked)
        }
    }, [media, onTimeUpdate, onVideoError, onVideoReady])

    return null
}
