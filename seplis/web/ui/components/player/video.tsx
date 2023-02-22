import { IPlayServerRequestSource } from '@seplis/interfaces/play-server'
import { guid } from '@seplis/utils'
import axios from 'axios'
import Hls, { ErrorData } from 'hls.js'
import { forwardRef, MutableRefObject, useEffect, useImperativeHandle, useRef, useState } from 'react'

interface IProps {
    source: IPlayServerRequestSource
    startTime?: number
    audio?: string
    resolutionWidth?: number
    children?: React.ReactNode
    onAutoPlayFailed?: () => void
    onTimeUpdate?: (time: number) => void
    onPause?: () => void
    onPlay?: () => void
    onLoadingState?: (loading: boolean) => void
}

export interface IVideoControls {
    sessionUUID: () => string
    setCurrentTime: (time: number) => void
    togglePlay: () => void
    paused: () => boolean
    setVolume: (volume: number) => void
    getVolume: () => number
}

export const Video = forwardRef<IVideoControls, IProps>(({
    source,
    startTime = 0,
    audio,
    resolutionWidth,
    children,
    onAutoPlayFailed,
    onTimeUpdate,
    onPause,
    onPlay,
    onLoadingState,
}: IProps, ref) => {
    const [sessionUUID, setSessionUUID] = useState<string>(guid())
    const videoElement = useRef<HTMLVideoElement>(null)
    const hls = useRef<Hls>(null)
    const baseTime = useRef<number>(startTime)
    const prevSource = useRef(source)
    const prevAudio = useRef(audio)
    const prevResolutionWidth = useRef(resolutionWidth)

    useImperativeHandle(ref, () => ({
        sessionUUID: () => sessionUUID,
        setCurrentTime: (time: number) => setCurrentTime(time, videoElement.current, setSessionUUID, baseTime, onTimeUpdate),
        togglePlay: () => togglePlay(videoElement.current),
        paused: () => videoElement.current.paused,
        setVolume: (volume: number) => videoElement.current.volume = volume,
        getVolume: () => videoElement.current.volume
    }), [videoElement.current])

    useEffect(() => {
        if ((prevSource.current == source) && (prevAudio.current == audio) && (prevResolutionWidth.current == resolutionWidth))
            return
        baseTime.current = getCurrentTime(videoElement.current, baseTime.current)
        setSessionUUID(guid())
    }, [source, audio, resolutionWidth])

    useEffect(() => {
        const url = getPlayUrl({
            videoElement: videoElement.current,
            resolutionWidth: resolutionWidth,
            sessionUUID: sessionUUID,
            audio: audio,
            source: source,
            startTime: Math.round(baseTime.current),
        })
        
        if (!Hls.isSupported()) {
            videoElement.current.src = url
            videoElement.current.load()
            videoElement.current.play().catch(() => {
                if (onAutoPlayFailed) onAutoPlayFailed()
            })
        } else {
            if (hls.current) hls.current.destroy()
            hls.current = new Hls({
                startLevel: 0,
                manifestLoadingTimeOut: 30000,
                maxMaxBufferLength: 30,
                debug: false,
            })
            hls.current.loadSource(url)
            hls.current.attachMedia(videoElement.current)
            hls.current.on(Hls.Events.MANIFEST_PARSED, () => {
                videoElement.current.play().catch(() => {
                    if (onAutoPlayFailed) onAutoPlayFailed()
                })
            })
            if (onHlsError)
                hls.current.on(Hls.Events.ERROR, (e, data) => { onHlsError(videoElement.current, hls.current, data, setSessionUUID) })
        }
        
        let t = setInterval(() => {
            axios.get(`${source.request.play_url}/keep-alive/${sessionUUID}`).catch(e => {
                if (e.response.status == 404) {
                    clearInterval(t)
                    baseTime.current = getCurrentTime(videoElement.current, baseTime.current)
                }
            })
        }, 4000)

        return () => {
            clearInterval(t)
            if (hls.current) hls.current.destroy()
            if (sessionUUID)
                axios.get(`${source.request.play_url}/close-session/${sessionUUID}`).catch(() => { })
        }
    }, [sessionUUID])
    

    return <video
        ref={videoElement}
        onTimeUpdate={(e) => {
            if (onTimeUpdate) onTimeUpdate(getCurrentTime(e.currentTarget, baseTime.current))
        }}
        onPause={() => onPause && onPause()}
        onPlay={() => {
            if (onPlay) onPlay()
            onLoadingState(false)
        }}
        onStalled={() => onLoadingState && onLoadingState(true)}
        onWaiting={() => onLoadingState && onLoadingState(true)}
        onPlaying={() => onLoadingState && onLoadingState(false)}
        onCanPlayThrough={() => onLoadingState && onLoadingState(false)}
        onError={(event) => {
            if (event.currentTarget.error.code == event.currentTarget.error.MEDIA_ERR_DECODE)
                handleMediaError(videoElement.current, hls.current)
        }}
        width="100%"
        style={{ position: 'fixed', height: '100%' }}
        controls={false}
        preload="none"
        crossOrigin="annonymous"
    >
        {children}
    </video>
})


function togglePlay(video: HTMLVideoElement) {
    if (video.paused)
        video.play()
    else
        video.pause()
}


function setCurrentTime(time: number, videoElement: HTMLVideoElement, setSessionUUID: (id: string) => void, baseTime: MutableRefObject<number>, onTimeUpdate: (n: number) => void) {
    if (videoElement.seekable.length <= 1 || videoElement.seekable.end(0) <= 1) {
        // If we are transcoding, check if we have transcoded enough to not have to start a new session
        const transcodedDuration = baseTime.current + videoElement.duration
        if ((time < baseTime.current) || (time > transcodedDuration)) {
            videoElement.pause()
            baseTime.current = time
            if (onTimeUpdate) onTimeUpdate(time)
            setSessionUUID(guid())
            videoElement.play()
        } else {
            videoElement.currentTime = time - baseTime.current
        }
    } else {
        videoElement.currentTime = time
    }
}


function getPlayUrl({ videoElement, source, startTime, audio, resolutionWidth, sessionUUID }: { videoElement: HTMLVideoElement, source: IPlayServerRequestSource, startTime: number, audio: string, resolutionWidth: number, sessionUUID: string }) {
    const videoCodecs = getSupportedVideoCodecs(videoElement)
    if (videoCodecs.length == 0)
        throw new Error('No supported codecs')
    return `${source.request.play_url}/transcode` +
        `?play_id=${source.request.play_id}` +
        `&source_index=${source.source.index}` +
        `&session=${sessionUUID}` +
        `&start_time=${startTime || 0}` +
        `&audio_lang=${audio || ''}` +
        `&width=${resolutionWidth || ''}` +
        `&supported_video_codecs=${String(videoCodecs)}` +
        `&transcode_video_codec=${videoCodecs[0]}` +
        //`&client_width=${this.getScreenWidth()}`+
        `&supported_audio_codecs=aac` +
        `&transcode_audio_codec=aac` +
        `&supported_pixel_formats=yuv420p` +
        `&transcode_pixel_format=yuv420p` +
        `&format=hls`
}


function getSupportedVideoCodecs(videoElement: HTMLVideoElement) {
    const types: { [key: string]: string } = {
        //'video/mp4; codecs="hvc1"': 'hevc',
        'video/mp4; codecs="avc1.42E01E"': 'h264',
    }
    const codecs = []
    for (const key in types) {
        if (videoElement.canPlayType(key))
            codecs.push(types[key])
    }
    return codecs
}


function onHlsError(videoElement: HTMLVideoElement, hls: Hls, data: ErrorData, setSessionUUID: (v: string) => void) {
    console.warn(data)
    if (data.fatal) {
        switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
                console.log('hls.js fatal network error encountered, try to recover')
                hls.startLoad()
                break
            case Hls.ErrorTypes.MEDIA_ERROR:
                console.log('hls.js fatal media error encountered, try to recover')
                hls.swapAudioCodec()
                handleMediaError(videoElement, hls)
                break
            default:
                console.log('hls.js could not recover')
                hls.destroy()
                break
        }
    }
}


function handleMediaError(videoElement: HTMLVideoElement, hls: Hls) {
    if (hls)
        hls.recoverMediaError()
    videoElement.play()
}


function getCurrentTime(videoElement: HTMLVideoElement, baseTime: number) {
    let time = videoElement.currentTime
    if (videoElement.seekable.length <= 1 || videoElement.seekable.end(0) <= 1)
        time += baseTime
    return Math.round(time)
}