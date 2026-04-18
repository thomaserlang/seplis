import type { Video as VideoMedia } from '@videojs/core'
import { useMedia } from '@videojs/react'
import Hls from 'hls.js'
import { useEffect } from 'react'
import type { PlayerVideoHlsProps } from './player-video.types'

export const hasNativeHls = (() => {
    const video = document.createElement('video')
    return !!video.canPlayType('application/vnd.apple.mpegurl')
})()

export function HlsJsPlayer({ src, startTimeRef }: PlayerVideoHlsProps): null {
    const media = useMedia() as VideoMedia | null

    useEffect(() => {
        if (!media) return
        const hls = new Hls({ startPosition: startTimeRef.current })
        hls.loadSource(src)
        hls.attachMedia(media as unknown as HTMLVideoElement)
        return () => {
            hls.destroy()
        }
    }, [media, src, startTimeRef])

    return null
}
