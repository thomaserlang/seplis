import { Box, Flex, forwardRef, Heading, IconButton, IconButtonProps, Popover, PopoverArrow, PopoverBody, PopoverContent, PopoverTrigger, Spinner, Stack, useBoolean, useDisclosure } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlayServerRequestSources } from '@seplis/interfaces/play-server'
import { secondsToTime } from '@seplis/utils'
import { ReactNode, useEffect, useRef, useState } from 'react'
import { FaArrowsAlt, FaCog, FaExpand, FaPause, FaPlay, FaRedo, FaStepForward, FaTimes, FaUndo, FaVolumeDown, FaVolumeOff, FaVolumeUp } from 'react-icons/fa'
import { Link } from 'react-router-dom'
import { pickStartSource } from './pick-source'
import { useGetPlayServers } from './request-play-servers'
import Slider from './slider'
import { IVideoControls, Video } from './video'
import VolumeBar from './volume-bar'

export interface IPlayNextProps {
    title: string
    url: string
}

export interface IPlayerProps {
    getPlayServersUrl: string,
    startTime: number
    loading: boolean
    title?: string,
    playNext?: IPlayNextProps
    onTimeUpdate: (time: number, duration: number) => void
}

export default function Player({ getPlayServersUrl, title, startTime = 0, playNext, loading, onTimeUpdate }: IPlayerProps) {
    const playServers = useGetPlayServers(getPlayServersUrl)

    if (playServers.isLoading || playServers.isFetching || loading)
        return <Loading />

    if (!playServers.data || (playServers.data.length === 0))
        return <h1>No play server has this content available</h1>

    return <VideoPlayer
        key={getPlayServersUrl}
        playServerSources={playServers.data}
        title={title}
        startTime={startTime}
        playNext={playNext}
        onTimeUpdate={onTimeUpdate}
    />
}


interface IVideoPlayerProps {
    playServerSources: IPlayServerRequestSources[]
    title: string
    startTime: number
    playNext: IPlayNextProps
    onTimeUpdate: (time: number, duration: number) => void
}

function VideoPlayer({ playServerSources, title, startTime, playNext, onTimeUpdate }: IVideoPlayerProps) {
    const [requestSource, setRequestSource] = useState<IPlayServerRequestSource>(
        () => pickStartSource(playServerSources))
    const [time, setTime] = useState(startTime)
    const [paused, setPaused] = useState(false)
    const [loading, setLoading] = useState(true)
    const [showBigPlay, setShowBigPlay] = useState(false)
    const [showControls, setShowControls] = useState(1)
    const hideControlsTimer = useRef<NodeJS.Timeout>()
    const videoControls = useRef<IVideoControls>()
    const wrapper = useRef<HTMLDivElement>()

    useEffect(() => {
        if (showControls === 0) return
        clearTimeout(hideControlsTimer.current)
        hideControlsTimer.current = setTimeout(() => {
            setShowControls(0)
        }, 4000)
        return () => {
            clearTimeout(hideControlsTimer.current)
        }
    }, [showControls])

    useEffect(() => {
        videoControls.current.setVolume(parseFloat(localStorage.getItem('volume')) || 0.5)

        const keyDown = (e: globalThis.KeyboardEvent) => {
            if (e.code == 'Space')
                videoControls.current.togglePlay()
        }
        document.addEventListener('keydown', keyDown)
        return () => document.removeEventListener('keydown', keyDown)
    }, [])

    return <Box
        ref={wrapper}
        position="fixed"
        width="100%"
        height="100%"
        left="0"
        top="0"
        backgroundColor="#000"
        onMouseMove={() => { setShowControls(showControls + 1) }}
        onTouchMove={() => { setShowControls(showControls + 1) }}
        onClick={() => {
            if (paused) return
            if (showControls > 0)
                setShowControls(0)
            else
                setShowControls(showControls + 1)
        }}
    >
        <Video
            ref={videoControls}
            source={requestSource}
            startTime={startTime}
            onTimeUpdate={(time) => {
                onTimeUpdate(time, requestSource.source.duration)
                setTime(time)
                if ((showControls > 0) && (!hideControlsTimer.current))
                    setShowControls(showControls + 1)
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
        />


        {!paused && loading && <Loading />}
        {showBigPlay && <BigPlay onClick={() => videoControls.current.togglePlay()} />}

        {(showControls || paused) && <ControlsTop>
            <PlayButton aria-label="back" icon={<FaTimes />} />
        </ControlsTop>}

        {(showControls || paused) && <ControlsBottom>
            <Heading fontSize="26px" fontWeight="400">{title}</Heading>

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
                <Box fontSize="14px">{secondsToTime(requestSource.source.duration)}</Box>
            </Flex>

            <Flex gap="0.5rem">
                {paused ?
                    <PlayButton aria-label="Play" icon={<FaPlay />} onClick={() => videoControls.current.togglePlay()} /> :
                    <PlayButton aria-label="Pause" icon={<FaPause />} onClick={() => videoControls.current.togglePlay()} />
                }

                <PlayButton aria-label="Rewind 15 seconds" icon={<FaUndo />} onClick={() => videoControls.current.setCurrentTime(time - 15)} />
                <PlayButton aria-label="Forward 15 seconds" icon={<FaRedo />} onClick={() => videoControls.current.setCurrentTime(time + 15)} />
                <VolumeButton videoControls={videoControls.current} />

                <Flex style={{ marginLeft: 'auto' }} gap="0.5rem">
                    {playNext && <PlayNext {...playNext} />}
                    <PlayButton aria-label="Settings" icon={<FaCog />} />
                    <FullscreenButton wrapper={wrapper.current} />
                </Flex>
            </Flex>
        </ControlsBottom>}
    </Box>
}


function FullscreenButton({ wrapper }: { wrapper: HTMLElement }) {
    const [fullscreen, setFullscreen] = useState(false)
    return <>{fullscreen ?
        <PlayButton aria-label="Open fullscreen" icon={<FaExpand />} onClick={() => fullscreenToggle(wrapper, setFullscreen)} /> :
        <PlayButton aria-label="Exit fullscreen" icon={<FaArrowsAlt />} onClick={() => fullscreenToggle(wrapper, setFullscreen)} />
    }</>
}


function VolumeButton({ videoControls }: { videoControls: IVideoControls }) {
    const [volume, setVolume] = useState(parseFloat(localStorage.getItem('volume')) || 0.5)

    function volumeIcon() {
        if (volume >= 0.5)
            return <FaVolumeUp />
        if (volume >= 0.1)
            return <FaVolumeDown />
        return <FaVolumeOff />
    }
    return <Popover
        returnFocusOnClose={false}
    >
        <PopoverTrigger>
            <PlayButton aria-label="Volume" icon={volumeIcon()} />
        </PopoverTrigger>
        <PopoverContent width="auto" padding="1rem">
            <PopoverArrow />
            <PopoverBody>
                <VolumeBar defaultVolume={volume} onChange={(volume) => {
                    localStorage.setItem('volume', volume.toString())
                    videoControls.setVolume(volume)
                    setVolume(volume)
                }} />
            </PopoverBody>
        </PopoverContent>
    </Popover>
}


function PlayNext({ title, url }: IPlayNextProps) {
    return <Link to={url} title={title}>
        <PlayButton aria-label={`Play ${title}`} icon={<FaStepForward />} />
    </Link>
}


const PlayButton = forwardRef<IconButtonProps, 'button'>((props, ref) => {
    return <IconButton
        ref={ref}
        {...props}
        size="lg"
        fontSize="28px"
    />
})


function ControlsTop({ children }: { children: ReactNode }) {
    return <Flex
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
}


function ControlsBottom({ children }: { children: ReactNode }) {
    return <Flex
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
}


function Loading() {
    return <Flex
        position="absolute"
        height="100%"
        width="100%"
        justifyContent="center"
        align="center"
        pointerEvents="none"
    >
        <Spinner color="#36c" width="5rem" height="5rem" />
    </Flex>
}


function BigPlay({ onClick }: { onClick: () => void }) {
    return <Flex
        position="absolute"
        height="100%"
        width="100%"
        justifyContent="center"
        align="center"
    >
        <IconButton variant="" aria-label="Play" icon={<FaPlay />} onClick={onClick} fontSize="100px" />
    </Flex>
}


function fullscreenToggle(element: HTMLElement, setFullscreen: (fullscreen: boolean) => void) {
    if (!document.fullscreenElement) {
        if ((element as any).enterFullscreen) {
            (element as any).enterFullscreen()
        } else if ((element as any).requestFullScreen) {
            (element as any).requestFullScreen()
        } else if ((element as any).mozRequestFullScreen) {
            (element as any).mozRequestFullScreen()
        } else if ((element as any).webkitRequestFullScreen) {
            (element as any).webkitRequestFullScreen((Element as any).ALLOW_KEYBOARD_INPUT)
        } else if ((element as any).webkitEnterFullscreen) {
            (element as any).webkitEnterFullscreen()
        }
        setFullscreen(true)
    } else {
        if ((document as any).cancelFullScreen) {
            (document as any).cancelFullScreen()
        } else if ((document as any).mozCancelFullScreen) {
            (document as any).mozCancelFullScreen()
        } else if ((document as any).webkitCancelFullScreen) {
            (document as any).webkitCancelFullScreen()
        }
        setFullscreen(false)
    }
}