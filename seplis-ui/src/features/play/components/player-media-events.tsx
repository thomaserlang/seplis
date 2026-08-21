import type { Video as VideoMedia } from '@videojs/media'
import { useMedia } from '@videojs/react'
import { useEffect, useEffectEvent, useRef } from 'react'
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
    const emitVideoReady = useEffectEvent(() => onVideoReady?.())
    const emitVideoError = useEffectEvent(() => onVideoError?.())
    const emitTimeUpdate = useEffectEvent(
        (currentTime: number, duration: number) =>
            onTimeUpdate?.(currentTime, duration),
    )

    useEffect(() => {
        if (!media) return

        const handleCanPlay = () => emitVideoReady()
        const handleError = () => emitVideoError()
        const handleTimeUpdate = () => {
            if (!media.duration) return
            emitTimeUpdate(media.currentTime, media.duration)
        }
        const handleVolumeChange = () => {
            localStorage.setItem(
                'player-volume',
                String(Math.round(media.volume * 100) / 100),
            )
        }
        const handleMetadataLoaded = () => {
            const startTime = resumeTimeRef.current
            if (
                startTime > 0 &&
                Math.abs(media.currentTime - startTime) > 0.5
            ) {
                media.currentTime = startTime
            }
        }

        const savedVolume = localStorage.getItem('player-volume')
        media.volume = savedVolume !== null ? parseFloat(savedVolume) : 0.5

        media.addEventListener('canplay', handleCanPlay)
        media.addEventListener('error', handleError)
        media.addEventListener('timeupdate', handleTimeUpdate)
        media.addEventListener('volumechange', handleVolumeChange)
        media.addEventListener('loadedmetadata', handleMetadataLoaded)

        if (media.readyState >= HTMLMediaElement.HAVE_METADATA) {
            handleMetadataLoaded()
        }
        if (media.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) {
            handleCanPlay()
        }

        return () => {
            media.removeEventListener('canplay', handleCanPlay)
            media.removeEventListener('error', handleError)
            media.removeEventListener('timeupdate', handleTimeUpdate)
            media.removeEventListener('volumechange', handleVolumeChange)
            media.removeEventListener('loadedmetadata', handleMetadataLoaded)
        }
    }, [media])

    return null
}
