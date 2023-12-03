import { IPlayServerRequestMedia, IPlayServerRequestSource, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'
import Hls from 'hls.js'
import { forwardRef, MutableRefObject, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { detect } from 'detect-browser'

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
    sessionUUID: () => string
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
    const [sessionUUID, setSessionUUID] = useState<string>(uuidv4())
    const videoElement = useRef<HTMLVideoElement>(null)
    const hls = useRef<Hls>(null)
    const baseTime = useRef<number>(startTime)
    const recoverTime = useRef<number>(startTime)
    const prevRequestSource = useRef(requestSource)
    const prevAudioSource = useRef(audioSource)
    const prevResolutionWidth = useRef(resolutionWidth)
    const changeTimeDebounce = useRef<NodeJS.Timeout>(null)
    const requestMedia = useRef<IPlayServerRequestMedia>(null)

    useImperativeHandle(ref, () => ({
        sessionUUID: () => sessionUUID,
        setCurrentTime: (time: number) => setCurrentTime(time, videoElement.current, setSessionUUID, baseTime, onTimeUpdate, onLoadingState, changeTimeDebounce, requestMedia.current),
        getCurrentTime: () => getCurrentTime(videoElement.current, requestMedia.current, baseTime.current),
        skipSeconds: (seconds: number = 15) => {
            let t = getCurrentTime(videoElement.current, requestMedia.current, baseTime.current) + seconds
            if (t > requestSource.source.duration)
                t = requestSource.source.duration
            if (t < 0) t = 0
            setCurrentTime(t, videoElement.current, setSessionUUID, baseTime, onTimeUpdate, onLoadingState, changeTimeDebounce, requestMedia.current)
        },
        togglePlay: () => togglePlay(videoElement.current),
        paused: () => videoElement.current.paused,
        setVolume: (volume: number) => videoElement.current.volume = volume,
        getVolume: () => videoElement.current.volume,
        toggleFullscreen: () => toggleFullscreen(videoElement.current)
    }), [videoElement.current])

    useEffect(() => {
        if ((prevRequestSource.current == requestSource) && (prevAudioSource.current == audioSource) &&
            (prevResolutionWidth.current == resolutionWidth))
            return
        baseTime.current = getCurrentTime(videoElement.current, requestMedia.current, baseTime.current)
        setSessionUUID(uuidv4())
    }, [requestSource, audioSource, resolutionWidth])

    useEffect(() => {
        if (!sessionUUID)
            return

        const recover = () => {
            baseTime.current = recoverTime.current

            if (videoElement.current.paused) {
                if (onPause) onPause()
                setSessionUUID(null)
            } else {
                if (onLoadingState) onLoadingState(true)
                setSessionUUID(uuidv4())
            }
        }

        const start = async () => {
            requestMedia.current = await getPlayRequestMedia({
                videoElement: videoElement.current,
                resolutionWidth: resolutionWidth,
                sessionUUID: sessionUUID,
                audio: audioSource && `${audioSource.language}:${audioSource.index}`,
                requestSource: requestSource,
                startTime: baseTime.current,
            })
            baseTime.current = requestMedia.current.transcode_start_time

            if (!Hls.isSupported() || requestMedia.current.can_direct_play) {
                if (requestMedia.current.can_direct_play) {
                    videoElement.current.src = requestMedia.current.direct_play_url
                    videoElement.current.currentTime = baseTime.current
                } else {
                    videoElement.current.src = requestMedia.current.transcode_url
                }
                videoElement.current.load()
                videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed())
            } else {
                if (hls.current) hls.current.destroy()
                hls.current = new Hls({
                    startLevel: 0,
                    startPosition: 0,
                    manifestLoadingTimeOut: 30000,
                    maxMaxBufferLength: 30,
                    debug: false,
                })
                hls.current.loadSource(requestMedia.current.transcode_url)
                hls.current.attachMedia(videoElement.current)
                hls.current.on(Hls.Events.MANIFEST_PARSED, () =>
                    videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed()))
                hls.current.on(Hls.Events.ERROR, (e, data) => {
                    console.warn(data)
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            if (!data.fatal && ((data.response as any)?.code !== 404))
                                return
                            console.log('hls.js fatal network error encountered, try to recover')
                            recover()
                            break
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            if (!data.fatal)
                                return
                            console.log('hls.js fatal media error encountered, try to recover')
                            if (onPause) onPause()
                            if (onLoadingState) onLoadingState(true)
                            hls.current.swapAudioCodec()
                            hls.current.recoverMediaError()
                            videoElement.current.play().catch(() => { })
                            break
                        default:
                            if (!data.fatal) return
                            console.log('hls.js could not recover')
                            recover()
                            break
                    }
                })
            }
        }
        start().catch((e) => {
            console.error(e)
        })

        const t = setInterval(() => {
            if (requestMedia.current.can_direct_play)
                return
            axios.get(`${requestSource.request.play_url}/keep-alive/${sessionUUID}`).catch(e => {
                if (e.response.status == 404) {
                    clearInterval(t)
                    if (!Hls.isSupported())
                        recover()
                }
            })
        }, 4000)

        return () => {
            clearInterval(t)
            if (hls.current) hls.current.destroy()
            if (sessionUUID && !requestMedia.current.can_direct_play)
                axios.get(`${requestSource.request.play_url}/close-session/${sessionUUID}`).catch(() => { })
        }
    }, [sessionUUID])

    return <>
        <video
            ref={videoElement}
            onTimeUpdate={() => {
                const t = getCurrentTime(videoElement.current, requestMedia.current, baseTime.current)
                if (t !== baseTime.current)
                    recoverTime.current = t
                if (onTimeUpdate) onTimeUpdate(t)
            }}
            onPause={() => {
                if (onPause) onPause()
                recoverTime.current = getCurrentTime(videoElement.current, requestMedia.current, baseTime.current)
            }}
            onPlay={() => {
                if (!sessionUUID)
                    setSessionUUID(uuidv4())
                if (onPlay) onPlay()
                if (onLoadingState) onLoadingState(false)
            }}
            onWaiting={() => onLoadingState && onLoadingState(true)}
            onLoadStart={() => onLoadingState && onLoadingState(true)}
            onPlaying={() => onLoadingState && onLoadingState(false)}
            onCanPlayThrough={() => onLoadingState && onLoadingState(false)}
            onLoadedData={() => onLoadingState && onLoadingState(false)}
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
        </video>
        {requestMedia.current &&
            <SetSubtitle
                videoElement={videoElement.current}
                requestSource={requestSource}
                startTime={requestMedia.current.can_direct_play ? 0 : baseTime.current}
                subtitleSource={subtitleSource}
                subtitleOffset={subtitleOffset}
                subtitleLinePosition={subtitleLinePosition}
            />}
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


function setCurrentTime(
    time: number,
    videoElement: HTMLVideoElement,
    setSessionUUID: (id: string) => void,
    baseTime: MutableRefObject<number>,
    onTimeUpdate: (n: number) => void,
    setLoadingState: (loading: boolean) => void,
    changeTimeDebounce: MutableRefObject<NodeJS.Timeout>,
    requestMedia: IPlayServerRequestMedia,
) {
    clearTimeout(changeTimeDebounce.current)
    changeTimeDebounce.current = setTimeout(() => {
        if (!requestMedia.can_direct_play) {
            if (setLoadingState) setLoadingState(true)
            if (onTimeUpdate) onTimeUpdate(time)
            // If we are still transcoding, check if we have transcoded enough to not have to start a new session
            if ((videoElement.duration === Infinity) || (time < baseTime.current) ||
                (time > (baseTime.current + videoElement.duration))) {
                videoElement.pause()
                baseTime.current = time
                setSessionUUID(uuidv4())
                videoElement.play()
            } else {
                videoElement.currentTime = time - baseTime.current
            }
        } else {
            videoElement.currentTime = time
        }
    }, 50)
}


async function getPlayRequestMedia({ videoElement, requestSource, startTime, audio, resolutionWidth, sessionUUID }:
    { videoElement: HTMLVideoElement, requestSource: IPlayServerRequestSource, startTime: number, audio: string, resolutionWidth: number, sessionUUID: string }) {
    const videoCodecs = getSupportedVideoCodecs(videoElement)
    if (videoCodecs.length == 0)
        throw new Error('No supported codecs')

    const r = await axios.get<IPlayServerRequestMedia>(`${requestSource.request.play_url}/request-media` +
        `?play_id=${requestSource.request.play_id}` +
        `&source_index=${requestSource.source.index}` +
        `&session=${sessionUUID}` +
        `&start_time=${startTime || 0}` +
        `&audio_lang=${audio || ''}` +
        `&width=${resolutionWidth || ''}` +
        `&supported_video_codecs=${String(videoCodecs)}` +
        `&transcode_video_codec=${videoCodecs[0]}` +
        //`&client_width=${this.getScreenWidth()}`+
        `&supported_audio_codecs=aac` +
        `&transcode_audio_codec=aac` +
        `&format=hls` +
        `&audio_channels=6` +
        `&supported_video_containers=${String(getSupportedVideoContainers())}`
    )
    r.data.transcode_url = requestSource.request.play_url + r.data.transcode_url
    r.data.direct_play_url = requestSource.request.play_url + r.data.direct_play_url
    return r.data
}


function getSupportedVideoColorBitDepth() {
    if (screen.colorDepth > 24)
        return 10
    return 8
}


function getSupportedVideoCodecs(videoElement: HTMLVideoElement) {
    const types: { [key: string]: string } = {
        'video/mp4; codecs="avc1.42E01E"': 'h264',
        'video/mp4; codecs="hvc1"': 'hevc',
        'video/mp4; codecs="hev1.1.6.L93.90"': 'hevc',
        'video/mp4; codecs="av01.0.08M.08"': 'av1',
    }
    const codecs = []
    for (const key in types)
        if (videoElement.canPlayType(key))
            codecs.push(types[key])
    return [...new Set(codecs)]
}


function getSupportedVideoContainers() {
    const browser = detect()
    switch (browser && browser.name) {
        case 'chrome':
            return ['webm', 'mp4']
    }
    return ['mp4']
}


function getCurrentTime(videoElement: HTMLVideoElement, requestMedia: IPlayServerRequestMedia, baseTime: number) {
    if (requestMedia.can_direct_play)
        return videoElement.currentTime
    return videoElement.currentTime + baseTime
}


function SetSubtitle({ videoElement, requestSource, subtitleSource, startTime, subtitleOffset = 0, subtitleLinePosition = 16 }:
    { videoElement: HTMLVideoElement, requestSource: IPlayServerRequestSource, subtitleSource?: IPlaySourceStream, startTime: number, subtitleOffset?: number, subtitleLinePosition?: number }) {

    useEffect(() => {
        if (!videoElement) return

        for (const track of videoElement.textTracks)
            track.mode = 'disabled'

        // Idk why but adding a new track too fast after disabling a previous one
        // makes the new one not show up
        setTimeout(() => {            
            for (const track of videoElement.textTracks)
                track.mode = 'disabled'

            const track = document.createElement("track")
            track.kind = "subtitles"
            track.label = subtitleSource.title
            track.srclang = subtitleSource.language
            track.src = `${requestSource.request.play_url}/subtitle-file` +
                `?play_id=${requestSource.request.play_id}` +
                `&source_index=${requestSource.source.index}` +
                `&start_time=${startTime + subtitleOffset}` +
                `&lang=${`${subtitleSource.language}:${subtitleSource.index}`}`
            track.default = true
            //@ts-ignore
            track.mode = 'showing'
            videoElement.appendChild(track)
        }, 100)
    }, [videoElement, requestSource?.request.play_id, subtitleSource?.index, startTime, subtitleOffset])

    useEffect(() => {
        if (!videoElement) return
        for (const track of videoElement.textTracks) {
            if (track.mode == 'showing')
                for (const cue of track.cues)
                    (cue as VTTCue).line = subtitleLinePosition
        }
    }, [subtitleLinePosition])

    return <></>
}
