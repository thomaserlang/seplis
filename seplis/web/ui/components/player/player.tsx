import {
    Box,
    Flex,
    forwardRef,
    Heading,
    IconButton,
    IconButtonProps,
    Popover,
    PopoverArrow,
    PopoverBody,
    PopoverContent,
    PopoverTrigger,
    Spinner,
} from '@chakra-ui/react'
import {
    IPlayServerRequestSource,
    IPlayServerRequestSources,
    IPlaySourceStream,
} from '@seplis/interfaces/play-server'
import { ReactNode, useCallback, useEffect, useRef, useState } from 'react'
import {
    FaArrowsAlt,
    FaExpand,
    FaPause,
    FaPlay,
    FaRedo,
    FaStepForward,
    FaTimes,
    FaUndo,
    FaVolumeDown,
    FaVolumeOff,
    FaVolumeUp,
} from 'react-icons/fa'
import { TbShareplay } from 'react-icons/tb'

import { isMobile, secondsToTime } from '@seplis/utils'
import { Link } from 'react-router-dom'
import FullErrorPage from '../full-page-error'
import { pickStartAudio } from './pick-audio-source'
import { getResolutionWidth } from './pick-quality'
import { pickStartSource } from './pick-source'
import { pickStartSubtitle } from './pick-subtitle-source'
import { useGetPlayServers } from './request-play-servers'
import { SettingsMenu } from './settings'
import Slider from './slider'
import { IVideoControls, Video } from './video'
import VolumeBar from './volume-bar'

export interface IPlayNextProps {
    title: string
    url: string
}

export interface IPlayerProps {
    getPlayServersUrl: string
    startTime: number
    loading: boolean
    title?: string
    playNext?: IPlayNextProps
    defaultAudio?: string
    defaultSubtitle?: string
    onClose?: () => void
    onTimeUpdate?: (time: number, duration: number) => void
    onAudioChange?: (source: IPlaySourceStream) => void
    onSubtitleChange?: (source: IPlaySourceStream) => void
}

export default function Player({
    getPlayServersUrl,
    title,
    startTime = 0,
    playNext,
    loading,
    defaultAudio,
    defaultSubtitle,
    onClose,
    onTimeUpdate,
    onAudioChange,
    onSubtitleChange,
}: IPlayerProps) {
    const playServers = useGetPlayServers(getPlayServersUrl)

    if (playServers.isLoading || playServers.isFetching || loading)
        return <Loading />

    if (!playServers.data || playServers.data.length === 0)
        return (
            <FullErrorPage message="No play server has this content available." />
        )

    return (
        <VideoPlayer
            key={getPlayServersUrl}
            playServers={playServers.data}
            title={title}
            startTime={startTime}
            playNext={playNext}
            onTimeUpdate={onTimeUpdate}
            defaultAudio={defaultAudio}
            defaultSubtitle={defaultSubtitle}
            onAudioChange={onAudioChange}
            onSubtitleChange={onSubtitleChange}
            onClose={onClose}
        />
    )
}

interface IVideoPlayerProps {
    playServers: IPlayServerRequestSources[]
    title: string
    startTime: number
    playNext: IPlayNextProps
    defaultAudio?: string
    defaultSubtitle?: string
    onClose?: () => void
    onTimeUpdate: (time: number, duration: number) => void
    onAudioChange?: (source: IPlaySourceStream) => void
    onSubtitleChange?: (source: IPlaySourceStream) => void
}

function VideoPlayer({
    playServers,
    title,
    startTime,
    playNext,
    defaultAudio,
    defaultSubtitle,
    onClose,
    onTimeUpdate,
    onAudioChange,
    onSubtitleChange,
}: IVideoPlayerProps) {
    const [requestSource, setRequestSource] =
        useState<IPlayServerRequestSource>(() => pickStartSource(playServers))
    const [resolutionWidth, setResolutionWidth] = useState<number>(
        getResolutionWidth(requestSource.source)
    )
    const [audioSource, setAudioSource] = useState<IPlaySourceStream>(() =>
        pickStartAudio(requestSource.source.audio, defaultAudio)
    )
    const [subtitleSource, setSubtitleSource] = useState<IPlaySourceStream>(
        () => pickStartSubtitle(requestSource.source.subtitles, defaultSubtitle)
    )
    const [forceTranscode, setForceTranscode] = useState<boolean>(
        getDefaultForceTranscode()
    )
    const [subtitleOffset, setSubtitleOffset] = useState<number>(0)
    const [time, setTime] = useState(startTime)
    const [paused, setPaused] = useState(false)
    const [loading, setLoading] = useState(true)
    const [showBigPlay, setShowBigPlay] = useState(false)
    const [controlsVisible, setControlsVisible] = useState(true)
    const hideControlsTimer = useRef<NodeJS.Timeout>()
    const videoControls = useRef<IVideoControls>()
    const boxRef = useRef(null)
    const [airplayAvailable, setAirplayAvailable] = useState<boolean>(false)

    const showControls = () => {
        setControlsVisible(true)
        clearTimeout(hideControlsTimer.current)
        hideControlsTimer.current = setTimeout(() => {
            setControlsVisible(false)
        }, 4000)
        return () => {
            clearTimeout(hideControlsTimer.current)
        }
    }

    const requestSourceChange = useCallback(
        (newRequestSource: IPlayServerRequestSource) => {
            setRequestSource(newRequestSource)
            setResolutionWidth(getResolutionWidth(newRequestSource.source))
            setAudioSource(
                pickStartAudio(newRequestSource.source.audio, defaultAudio)
            )
            setSubtitleSource(
                pickStartSubtitle(
                    newRequestSource.source.subtitles,
                    defaultSubtitle
                )
            )
        },
        [defaultAudio, defaultSubtitle]
    )

    useEffect(() => {
        videoControls.current.setVolume(
            parseFloat(localStorage.getItem('volume')) || 0.5
        )

        const keyDown = (e: globalThis.KeyboardEvent) => {
            showControls()
            if (e.code == 'Space') {
                videoControls.current.togglePlay()
                e.preventDefault()
            }
            if (e.code == 'ArrowLeft') {
                videoControls.current.skipSeconds(-15)
                e.preventDefault()
            }
            if (e.code == 'ArrowRight') {
                videoControls.current.skipSeconds(15)
                e.preventDefault()
            }
        }
        document.addEventListener('keydown', keyDown)
        return () => document.removeEventListener('keydown', keyDown)
    }, [])

    return (
        <Box
            id="player"
            position="fixed"
            width="100vw"
            height="100vh"
            left="0"
            top="0"
            backgroundColor="#000"
            ref={boxRef}
            onMouseMove={() => {
                showControls()
            }}
            onTouchMove={() => {
                showControls()
            }}
            onClick={() => {
                if (paused) return
                if (controlsVisible) setControlsVisible(false)
                else showControls()
            }}
        >
            <Video
                ref={videoControls}
                requestSource={requestSource}
                startTime={time}
                resolutionWidth={resolutionWidth}
                audioSource={audioSource}
                subtitleSource={subtitleSource}
                subtitleLinePosition={
                    controlsVisible || paused ? -4 : undefined
                }
                subtitleOffset={subtitleOffset}
                forceTranscode={forceTranscode}
                onTimeUpdate={(time) => {
                    onTimeUpdate?.(time, requestSource.source.duration)
                    setTime(time)
                    if (controlsVisible && !hideControlsTimer.current)
                        showControls()
                    if (loading) setLoading(false)
                }}
                onPause={() => setPaused(true)}
                onPlay={() => {
                    setPaused(false)
                    setShowBigPlay(false)
                }}
                onAutoPlayFailed={() => {
                    setPaused(true)
                    setShowBigPlay(true)
                }}
                onLoadingState={(loading) => setLoading(loading)}
                onAirplayAvailabilityChange={(available) =>
                    setAirplayAvailable(available)
                }
            />

            {!paused && loading && <Loading />}
            {showBigPlay && (
                <BigPlay onClick={() => videoControls.current.togglePlay()} />
            )}

            {(controlsVisible || paused) && (
                <ControlsTop>
                    <Flex gap="0.5rem" w="100%">
                        <PlayButton
                            aria-label="back"
                            icon={<FaTimes />}
                            onClick={() => {
                                onClose && onClose()
                            }}
                        />

                        {airplayAvailable && (
                            <div style={{ marginLeft: 'auto' }}>
                                <PlayButton
                                    aria-label="Airplay"
                                    icon={<TbShareplay />}
                                    onClick={() => {
                                        videoControls.current.showAirplayPicker()
                                    }}
                                />
                            </div>
                        )}
                    </Flex>
                </ControlsTop>
            )}

            {(controlsVisible || paused) && (
                <ControlsBottom>
                    <Heading fontSize="26px" fontWeight="400">
                        {title}
                    </Heading>

                    <Flex gap="0.5rem" align="center">
                        <Box fontSize="14px">{secondsToTime(time)}</Box>
                        <Flex grow="1">
                            <Slider
                                duration={requestSource.source.duration}
                                currentTime={time}
                                playRequest={requestSource.request}
                                onTimeChange={(time) => {
                                    videoControls.current.setCurrentTime(time)
                                }}
                            />
                        </Flex>
                        <Box fontSize="14px">
                            {secondsToTime(requestSource.source.duration)}
                        </Box>
                    </Flex>

                    <Flex gap="0.5rem">
                        <PlayButton
                            aria-label="Play or pause"
                            icon={paused ? <FaPlay /> : <FaPause />}
                            onClick={() => videoControls.current.togglePlay()}
                        />
                        <PlayButton
                            aria-label="Rewind 15 seconds"
                            icon={<FaUndo />}
                            onClick={() => {
                                videoControls.current.skipSeconds(-15)
                            }}
                        />
                        <PlayButton
                            aria-label="Forward 15 seconds"
                            icon={<FaRedo />}
                            onClick={() => {
                                videoControls.current.skipSeconds(15)
                            }}
                        />
                        {!isMobile && (
                            <VolumeButton
                                videoControls={videoControls.current}
                            />
                        )}

                        <Flex style={{ marginLeft: 'auto' }} gap="0.5rem">
                            {playNext && <PlayNext {...playNext} />}
                            <SettingsMenu
                                playServers={playServers}
                                requestSource={requestSource}
                                resolutionWidth={resolutionWidth}
                                audioSource={audioSource}
                                subtitleSource={subtitleSource}
                                subtitleOffset={subtitleOffset}
                                forceTranscode={forceTranscode}
                                onRequestSourceChange={requestSourceChange}
                                onResolutionWidthChange={setResolutionWidth}
                                onAudioSourceChange={(source) => {
                                    setAudioSource(source)
                                    if (onAudioChange) onAudioChange(source)
                                }}
                                onSubtitleSourceChange={(source) => {
                                    setSubtitleSource(source)
                                    if (onSubtitleChange)
                                        onSubtitleChange(source)
                                }}
                                onSubtitleOffsetChange={setSubtitleOffset}
                                onForceTranscodeChange={setForceTranscode}
                                containerRef={boxRef}
                            />
                            <FullscreenButton
                                videoControls={videoControls.current}
                            />
                        </Flex>
                    </Flex>
                </ControlsBottom>
            )}
        </Box>
    )
}

function FullscreenButton({
    videoControls,
}: {
    videoControls: IVideoControls
}) {
    const [fullscreen, setFullscreen] = useState(false)
    return fullscreen ? (
        <PlayButton
            aria-label="Open fullscreen"
            icon={<FaExpand />}
            onClick={() =>
                fullscreenToggle(
                    document.getElementById('player'),
                    videoControls,
                    setFullscreen
                )
            }
        />
    ) : (
        <PlayButton
            aria-label="Exit fullscreen"
            icon={<FaArrowsAlt />}
            onClick={() =>
                fullscreenToggle(
                    document.getElementById('player'),
                    videoControls,
                    setFullscreen
                )
            }
        />
    )
}

function VolumeButton({ videoControls }: { videoControls: IVideoControls }) {
    const [volume, setVolume] = useState(
        parseFloat(localStorage.getItem('volume')) || 0.5
    )

    function volumeIcon() {
        if (volume >= 0.5) return <FaVolumeUp />
        if (volume >= 0.1) return <FaVolumeDown />
        return <FaVolumeOff />
    }
    return (
        <Popover returnFocusOnClose={false}>
            <PopoverTrigger>
                <PlayButton aria-label="Volume" icon={volumeIcon()} />
            </PopoverTrigger>
            <PopoverContent width="auto" padding="1rem">
                <PopoverArrow />
                <PopoverBody>
                    <VolumeBar
                        defaultVolume={volume}
                        onChange={(volume) => {
                            localStorage.setItem('volume', volume.toString())
                            videoControls.setVolume(volume)
                            setVolume(volume)
                        }}
                    />
                </PopoverBody>
            </PopoverContent>
        </Popover>
    )
}

function PlayNext({ title, url }: IPlayNextProps) {
    return (
        <Link to={url} title={title} replace={true}>
            <PlayButton aria-label={`Play ${title}`} icon={<FaStepForward />} />
        </Link>
    )
}

export const PlayButton = forwardRef<IconButtonProps, 'button'>(
    (props, ref) => {
        return <IconButton ref={ref} {...props} size="lg" fontSize="28px" />
    }
)

function ControlsTop({ children }: { children: ReactNode }) {
    return (
        <Flex
            backgroundColor="rgba(0,0,0,0.8)"
            userSelect="none"
            position="fixed"
            top="0"
            bottom="auto"
            width="100%"
            padding="1rem"
            onClick={(e) => e.stopPropagation()}
        >
            {children}
        </Flex>
    )
}

function ControlsBottom({ children }: { children: ReactNode }) {
    return (
        <Flex
            backgroundColor="rgba(0,0,0,0.8)"
            userSelect="none"
            position="fixed"
            top="auto"
            bottom="0"
            width="100%"
            padding="1rem"
            direction="column"
            onClick={(e) => e.stopPropagation()}
        >
            {children}
        </Flex>
    )
}

function Loading() {
    return (
        <Flex
            position="absolute"
            height="100vh"
            width="100vw"
            justifyContent="center"
            align="center"
            pointerEvents="none"
        >
            <Spinner color="#36c" width="5rem" height="5rem" />
        </Flex>
    )
}

function BigPlay({ onClick }: { onClick: () => void }) {
    return (
        <Flex
            position="absolute"
            height="100%"
            width="100%"
            justifyContent="center"
            align="center"
        >
            <IconButton
                variant=""
                aria-label="Play"
                icon={<FaPlay />}
                onClick={onClick}
                fontSize="100px"
            />
        </Flex>
    )
}

function fullscreenToggle(
    element: HTMLElement,
    videoControls: IVideoControls,
    setFullscreen: (fullscreen: boolean) => void
) {
    if (!document.fullscreenElement) {
        if ((element as any).enterFullscreen) {
            ;(element as any).enterFullscreen()
        } else if ((element as any).requestFullScreen) {
            ;(element as any).requestFullScreen()
        } else if ((element as any).mozRequestFullScreen) {
            ;(element as any).mozRequestFullScreen()
        } else if ((element as any).webkitRequestFullScreen) {
            ;(element as any).webkitRequestFullScreen(
                (Element as any).ALLOW_KEYBOARD_INPUT
            )
        } else {
            videoControls.toggleFullscreen()
        }
        setFullscreen(true)
    } else {
        if ((document as any).cancelFullScreen) {
            ;(document as any).cancelFullScreen()
        } else if ((document as any).mozCancelFullScreen) {
            ;(document as any).mozCancelFullScreen()
        } else if ((document as any).webkitCancelFullScreen) {
            ;(document as any).webkitCancelFullScreen()
        }
        setFullscreen(false)
    }
}

function getDefaultForceTranscode() {
    // Currently there is an issue where Firefox won't start the video
    // if start time is above 0 and the video is not transcoded.
    return navigator.userAgent.includes('Firefox')
}
