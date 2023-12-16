import { IPlayServerRequestMedia, IPlayServerRequestSource, IPlaySourceStream } from '@seplis/interfaces/play-server'
import axios from 'axios'
import Hls from 'hls.js'
import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react'
import { browser } from '@seplis/utils'
import { useToast } from '@chakra-ui/react'

interface IProps {
    requestSource: IPlayServerRequestSource
    startTime?: number
    audioSource?: IPlaySourceStream,
    resolutionWidth?: number
    subtitleSource?: IPlaySourceStream
    children?: React.ReactNode
    subtitleOffset?: number
    subtitleLinePosition?: number
    onAutoPlayFailed?: () => void
    onTimeUpdate?: (time: number) => void
    onPause?: () => void
    onPlay?: () => void
    onLoadingState?: (loading: boolean) => void
}

export interface IVideoControls {
    setCurrentTime: (time: number) => void
    getCurrentTime: () => number
    skipSeconds: (seconds?: number) => void
    togglePlay: () => void
    toggleFullscreen: () => void
    paused: () => boolean
    setVolume: (volume: number) => void
    getVolume: () => number
}

export const Video = forwardRef<IVideoControls, IProps>(({
    requestSource,
    startTime = 0,
    audioSource,
    resolutionWidth,
    subtitleSource,
    children,
    subtitleOffset,
    subtitleLinePosition,
    onAutoPlayFailed,
    onTimeUpdate,
    onPause,
    onPlay,
    onLoadingState,
}: IProps, ref) => {
    const videoElement = useRef<HTMLVideoElement>(null)
    const hls = useRef<Hls>(null)
    const requestMedia = useRef<IPlayServerRequestMedia>(null)

    useImperativeHandle(ref, () => ({
        setCurrentTime: (time: number) => {
            videoElement.current.currentTime = time
            videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed())
            onTimeUpdate?.(time)
        },
        getCurrentTime: () => videoElement.current.currentTime,
        skipSeconds: (seconds: number = 15) => {
            videoElement.current.currentTime = videoElement.current.currentTime + seconds
            videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed())
            onTimeUpdate?.(videoElement.current.currentTime)
        },
        togglePlay: () => togglePlay(videoElement.current),
        paused: () => videoElement.current.paused,
        setVolume: (volume: number) => videoElement.current.volume = volume,
        getVolume: () => videoElement.current.volume,
        toggleFullscreen: () => toggleFullscreen(videoElement.current)
    }), [videoElement.current])

    useEffect(() => {
        const start = async () => {
            requestMedia.current = await getPlayRequestMedia({
                videoElement: videoElement.current,
                resolutionWidth: resolutionWidth,
                audio: audioSource && `${audioSource.language}:${audioSource.index}`,
                requestSource: requestSource,
                startTime: startTime,
            })
            if (!Hls.isSupported() || requestMedia.current.can_direct_play) {
                if (requestMedia.current.can_direct_play) {
                    videoElement.current.src = requestMedia.current.direct_play_url
                } else {
                    videoElement.current.src = requestMedia.current.hls_url
                }
                videoElement.current.currentTime = startTime
                videoElement.current.load()
                videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed())
            } else {
                hls.current = new Hls({
                    startPosition: startTime,
                    manifestLoadingTimeOut: 30000,
                    enableWorker: true,
                    lowLatencyMode: true,
                    backBufferLength: 90,
                })
                hls.current.loadSource(requestMedia.current.hls_url)
                hls.current.attachMedia(videoElement.current)
                hls.current.on(Hls.Events.MANIFEST_PARSED, () =>
                    videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed()))
                hls.current.on(Hls.Events.ERROR, (e, data) => {
                    console.warn(data)
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            if (!data.fatal) return
                            console.log('hls.js fatal network error encountered, try to recover')
                            break
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            if (!data.fatal)
                                return
                            console.log('hls.js fatal media error encountered')
                            break
                        default:
                            if (!data.fatal) return
                            console.log('hls.js could not recover')
                            break
                    }
                })
            }
        }
        start().catch((e) => {
            console.error(e)
        })

        const t = setInterval(() => {
            if ((requestMedia.current) && (!requestMedia.current?.can_direct_play))
                axios.get(requestMedia.current.keep_alive_url).catch(() => { })
        }, 4000)

        return () => {
            if (hls.current) {
                hls.current.destroy()
                hls.current = null
            }
            clearInterval(t)
            if ((requestMedia.current) && (!requestMedia.current.can_direct_play))
                axios.get(requestMedia.current.close_session_url).catch(() => { })
        }
    }, [requestSource, audioSource, resolutionWidth])

    return <>
        <video
            ref={videoElement}
            onTimeUpdate={() => {
                if (videoElement.current.readyState === 4)
                    onTimeUpdate?.(videoElement.current.currentTime)
            }}
            onPause={() => {
                onPause?.()
            }}
            onPlay={() => {
                onPlay?.()
                onLoadingState?.(false)
            }}
            onWaiting={() => onLoadingState?.(true)}
            onLoadStart={() => onLoadingState?.(true)}
            onPlaying={() => onLoadingState?.(false)}
            onCanPlayThrough={() => onLoadingState?.(false)}
            onLoadedData={() => onLoadingState?.(false)}
            onError={(event) => {
                if (event.currentTarget.error.code == event.currentTarget.error.MEDIA_ERR_DECODE)
                    hls.current.recoverMediaError()
            }}
            width="100%"
            style={{ position: 'fixed', height: '100%' }}
            controls={false}
            preload="none"
            crossOrigin="anonymous"
            playsInline
        >
            {children}
            <SetSubtitle
                videoElement={videoElement.current}
                requestSource={requestSource}
                subtitleSource={subtitleSource}
                subtitleOffset={subtitleOffset}
                subtitleLinePosition={subtitleLinePosition}
            />
        </video>
    </>
})

function togglePlay(video: HTMLVideoElement) {
    if (video.paused)
        video.play()
    else
        video.pause()
}


function toggleFullscreen(video: HTMLVideoElement) {
    if (!document.fullscreenElement) {
        if (video.requestFullscreen) {
            video.requestFullscreen();
        } else if ((video as any).webkitEnterFullscreen) {
            (video as any).webkitEnterFullscreen();
        }
    } else {
        if ((document as any).cancelFullScreen) {
            (document as any).cancelFullScreen()
        } else if ((document as any).webkitCancelFullScreen) {
            (document as any).webkitCancelFullScreen()
        }
    }
}


async function getPlayRequestMedia({ videoElement, requestSource, startTime, audio, resolutionWidth }:
    { videoElement: HTMLVideoElement, requestSource: IPlayServerRequestSource, startTime: number, audio: string, resolutionWidth: number }) {
    const videoCodecs = getSupportedVideoCodecs(videoElement)
    if (videoCodecs.length == 0)
        throw new Error('No supported codecs')

    const r = await axios.get<IPlayServerRequestMedia>(`${requestSource.request.play_url}/request-media` +
        `?play_id=${requestSource.request.play_id}` +
        `&source_index=${requestSource.source.index}` +
        `&start_time=${startTime || 0}` +
        `&audio_lang=${audio || ''}` +
        `&max_width=${resolutionWidth || ''}` +
        `&supported_video_codecs=${String(videoCodecs)}` +
        `&transcode_video_codec=${videoCodecs[0]}` +
        `&supported_audio_codecs=${String(getSupportedAudioCodecs(videoElement))}` +
        `&transcode_audio_codec=aac` +
        `&format=${Hls.isSupported() ? 'hls.js' : 'hls'}` +
        `&max_audio_channels=6` +
        `&supported_video_containers=${String(getSupportedVideoContainers())}`
    )
    if (r.data.hls_url.startsWith('/')) {
        r.data.hls_url = requestSource.request.play_url + r.data.hls_url
        r.data.direct_play_url = requestSource.request.play_url + r.data.direct_play_url
        r.data.keep_alive_url = requestSource.request.play_url + r.data.keep_alive_url
        r.data.close_session_url = requestSource.request.play_url + r.data.close_session_url
    }
    return r.data
}


function getSupportedVideoCodecs(videoElement: HTMLVideoElement) {
    const types: { [key: string]: string } = {
        'video/mp4; codecs="hvc1"': 'hevc',
        'video/mp4; codecs="hev1.1.6.L93.90"': 'hevc',
        'video/mp4; codecs="avc1.42E01E"': 'h264',
        'video/mp4; codecs="av01.0.08M.08"': 'av1',
    }
    const codecs: string[] = []
    for (const key in types)
        if (videoElement.canPlayType(key))
            codecs.push(types[key])
    return [...new Set(codecs)]
}


function getSupportedVideoContainers() {
    switch (browser.name) {
        case 'chrome':
        case 'edge-chromium':
            return ['webm', 'mp4']
    }
    return ['mp4']
}

function getSupportedAudioCodecs(videoElement: HTMLVideoElement) {
    const types: { [key: string]: string } = {
        'audio/aac': 'aac',
        'audio/mp4; codecs="ec-3"': 'eac3',
        'audio/mp4; codecs="ac-3"': 'ac3',
        'audio/mp4; codecs="ac-4"': 'ac4',
        'audio/mp4; codecs="opus"': 'opus',
        'audio/mp4; codecs="flac"': 'flac',
        'audio/mp4; codecs="dtsc"': 'dtsc',
        'audio/mp4; codecs="dtse"': 'dtse',
        'audio/mp4; codecs="dtsx"': 'dtsx',        
    }
    const codecs: string[] = []
    for (const key in types)
        if (videoElement.canPlayType(key))
            codecs.push(types[key])
    return [...new Set(codecs)]
}


function getSupportedHdrFormats(videoElement: HTMLVideoElement) {

}

interface IPropsSubtitle {
    videoElement: HTMLVideoElement
    requestSource: IPlayServerRequestSource
    subtitleSource?: IPlaySourceStream
    subtitleOffset?: number
    subtitleLinePosition?: number
}

function SetSubtitle({ 
    videoElement, 
    requestSource, 
    subtitleSource, 
    subtitleOffset = 0, 
    subtitleLinePosition = 16 
}: IPropsSubtitle) {
    const toast = useToast()
    const track = useRef<HTMLTrackElement>(null)
    const firstTrackLoad = useRef(true)

    useEffect(() => {
        if (!videoElement) return
        for (const track of videoElement.textTracks) {
            if (track.mode == 'showing')
                for (const cue of track.cues)
                    (cue as VTTCue).line = subtitleLinePosition
        }
    }, [subtitleLinePosition])

    useEffect(() => {
        firstTrackLoad.current = true
    }, [track])

    useEffect(() => {
        if (firstTrackLoad.current) {
            firstTrackLoad.current = false
            return
        }
        if (!track.current) return
        const id = toast({
            title: 'Loading subtitle',
            status: 'loading',
            duration: null,
            isClosable: true,
            position: 'top-right',
            variant: 'subtle',
        })
        track.current.onload = () => {
            toast.close(id)
        }
        return () => {
            toast.close(id)
        }
    }, [track, subtitleSource, requestSource, subtitleOffset])

    return <>
        {subtitleSource && <track
            ref={track}
            kind="subtitles"
            label={subtitleSource?.title || 'Unknown'}
            srcLang={subtitleSource?.language}
            src={`${requestSource.request.play_url}/subtitle-file` +
                `?play_id=${requestSource.request.play_id}` +
                `&source_index=${requestSource.source.index}` +
                `&offset=${subtitleOffset}` +
                `&lang=${`${subtitleSource.language}:${subtitleSource.index}`}`}
            default={true}
        />}
    </>
}
