import { IPlayServerRequestSource, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { guid } from '@seplis/utils'
import axios from 'axios'
import Hls, { ErrorData } from 'hls.js'
import { forwardRef, MutableRefObject, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { parse as vttParse } from '../../utils/srt-vtt-parser'
import { useQuery } from '@tanstack/react-query'

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
    togglePlay: () => void
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
    const [sessionUUID, setSessionUUID] = useState<string>(guid())
    const videoElement = useRef<HTMLVideoElement>(null)
    const hls = useRef<Hls>(null)
    const baseTime = useRef<number>(startTime)
    const prevRequestSource = useRef(requestSource)
    const prevAudioSource = useRef(audioSource)
    const prevResolutionWidth = useRef(resolutionWidth)

    useImperativeHandle(ref, () => ({
        sessionUUID: () => sessionUUID,
        setCurrentTime: (time: number) => setCurrentTime(time, videoElement.current, setSessionUUID, baseTime, onTimeUpdate),
        togglePlay: () => togglePlay(videoElement.current),
        paused: () => videoElement.current.paused,
        setVolume: (volume: number) => videoElement.current.volume = volume,
        getVolume: () => videoElement.current.volume,
    }), [videoElement.current])

    useEffect(() => {
        if ((prevRequestSource.current == requestSource) && (prevAudioSource.current == audioSource) &&
            (prevResolutionWidth.current == resolutionWidth))
            return
        baseTime.current = getCurrentTime(videoElement.current, baseTime.current)
        setSessionUUID(guid())
    }, [requestSource, audioSource, resolutionWidth])

    useEffect(() => {
        const url = getPlayUrl({
            videoElement: videoElement.current,
            resolutionWidth: resolutionWidth,
            sessionUUID: sessionUUID,
            audio: audioSource && `${audioSource.language}:${audioSource.index}`,
            requestSource: requestSource,
            startTime: Math.round(baseTime.current),
        })

        if (!Hls.isSupported()) {
            videoElement.current.src = url
            videoElement.current.load()
            videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed())
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
                videoElement.current.play().catch(() => onAutoPlayFailed && onAutoPlayFailed())
            })
            hls.current.on(Hls.Events.ERROR, (e, data) => onHlsError &&
                onHlsError(videoElement.current, hls.current, data))
        }

        let t = setInterval(() => {
            axios.get(`${requestSource.request.play_url}/keep-alive/${sessionUUID}`).catch(e => {
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
                axios.get(`${requestSource.request.play_url}/close-session/${sessionUUID}`).catch(() => { })
        }
    }, [sessionUUID])

    return <>
        <video
            ref={videoElement}
            onTimeUpdate={(e) => onTimeUpdate && onTimeUpdate(getCurrentTime(e.currentTarget, baseTime.current))}
            onPause={() => onPause && onPause()}
            onPlay={() => {
                if (onPlay) onPlay()
                onLoadingState(false)
            }}
            onWaiting={() => onLoadingState && onLoadingState(true)}
            onLoadStart={() => onLoadingState && onLoadingState(true)}
            onPlaying={() => onLoadingState && onLoadingState(false)}
            onCanPlayThrough={() => onLoadingState && onLoadingState(false)}
            onLoadedData={() => onLoadingState && onLoadingState(false)}
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
        <SetSubtitle
            videoElement={videoElement.current}
            requestSource={requestSource}
            startTime={baseTime.current}
            subtitleSource={subtitleSource}
            subtitleOffset={subtitleOffset}
            subtitleLinePosition={subtitleLinePosition}
        />
    </>
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


function getPlayUrl({ videoElement, requestSource, startTime, audio, resolutionWidth, sessionUUID }: { videoElement: HTMLVideoElement, requestSource: IPlayServerRequestSource, startTime: number, audio: string, resolutionWidth: number, sessionUUID: string }) {
    const videoCodecs = getSupportedVideoCodecs(videoElement)
    if (videoCodecs.length == 0)
        throw new Error('No supported codecs')
    return `${requestSource.request.play_url}/transcode` +
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


function onHlsError(videoElement: HTMLVideoElement, hls: Hls, data: ErrorData) {
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
    if (hls) hls.recoverMediaError()
    videoElement.play()
}


function getCurrentTime(videoElement: HTMLVideoElement, baseTime: number) {
    let time = videoElement.currentTime
    if (videoElement.seekable.length <= 1 || videoElement.seekable.end(0) <= 1)
        time += baseTime
    return Math.round(time)
}


function SetSubtitle({ videoElement, requestSource, subtitleSource, startTime, subtitleOffset = 0, subtitleLinePosition = 16 }: { videoElement: HTMLVideoElement, requestSource: IPlayServerRequestSource, subtitleSource?: IPlaySourceStream, startTime: number, subtitleOffset?: number, subtitleLinePosition?: number }) {
    const { data } = useQuery(['subtitle', requestSource?.request.play_id, subtitleSource?.index], async () => {
        if (!subtitleSource)
            return null
        const result = await axios.get<string>(`${requestSource.request.play_url}/subtitle-file` +
            `?play_id=${requestSource.request.play_id}` +
            `&source_index=${requestSource.source.index}` +
            `&lang=${`${subtitleSource.language}:${subtitleSource.index}`}`)
        return vttParse(result.data)
    })

    useEffect(() => {
        if (!videoElement) return

        for (const track of videoElement.textTracks) {
            track.mode = 'disabled'
        }
        
        if (!data) return

        // Idk why but adding a new track too fast after disabling a previous one
        // makes the new one not show up
        setTimeout(() => {
            const textTrack = videoElement.addTextTrack('subtitles', subtitleSource.title, subtitleSource.language)
            textTrack.mode = 'showing'
            for (const cue of data.entries) {
                const vtt = new VTTCue(
                    ((cue.from / 1000) - startTime) + subtitleOffset, 
                    ((cue.to / 1000) - startTime) + subtitleOffset, 
                    cue.text
                )
                vtt.line = subtitleLinePosition
                textTrack.addCue(vtt)
            }
        }, 100)
    }, [data, startTime, subtitleOffset])

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