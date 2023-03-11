import { Box, Flex, forwardRef, Heading, IconButton, IconButtonProps, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Popover, PopoverArrow, PopoverBody, PopoverContent, PopoverTrigger, Spinner, Stack, useBoolean, useDisclosure } from '@chakra-ui/react'
import { IPlayServerRequestSource, IPlayServerRequestSources, IPlaySourceStream } from '@seplis/interfaces/play-server'
import { secondsToTime } from '@seplis/utils'
import { ReactNode, useEffect, useRef, useState } from 'react'
import { FaArrowsAlt, FaCog, FaExpand, FaPause, FaPlay, FaRedo, FaStepForward, FaTimes, FaUndo, FaVolumeDown, FaVolumeOff, FaVolumeUp } from 'react-icons/fa'
import { Link } from 'react-router-dom'
import { pickStartAudio } from './pick-audio-source'
import { getDefaultResolutionWidth } from './pick-quality'
import { pickStartSource } from './pick-source'
import { pickStartSubtitle } from './pick-subtitle-source'
import { useGetPlayServers } from './request-play-servers'
import { ISettingsProps, Settings } from './settings'
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
    defaultAudio?: string
    defaultSubtitle?: string
    onClose?: () => void,
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

    if (!playServers.data || (playServers.data.length === 0))
        return <h1>No play server has this content available</h1>

    return <VideoPlayer
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
    const [requestSource, setRequestSource] = useState<IPlayServerRequestSource>(
        () => pickStartSource(playServers))
    const [resolutionWidth, setResolutionWidth] = useState<number>(getDefaultResolutionWidth())
    const [audioSource, setAudioSource] = useState<IPlaySourceStream>(() => pickStartAudio(requestSource, defaultAudio))
    const [subtitleSource, setSubtitleSource] = useState<IPlaySourceStream>(() => pickStartSubtitle(requestSource, defaultSubtitle))
    const [subtitleOffset, setSubtitleOffset] = useState<number>(0)
    const [time, setTime] = useState(startTime)
    const [paused, setPaused] = useState(false)
    const [loading, setLoading] = useState(true)
    const [showBigPlay, setShowBigPlay] = useState(false)
    const [showControls, setShowControls] = useState(true)
    const hideControlsTimer = useRef<NodeJS.Timeout>()
    const videoControls = useRef<IVideoControls>()

    const startHideControlsTimer = () => {
        if (!showControls) 
            setShowControls(true)
        clearTimeout(hideControlsTimer.current)
        hideControlsTimer.current = setTimeout(() => {
            setShowControls(false)
        }, 4000)
        return () => {
            clearTimeout(hideControlsTimer.current)
        }
    }

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
        position="fixed"
        width="100%"
        height="100%"
        left="0"
        top="0"
        backgroundColor="#000"
        onMouseMove={() => { startHideControlsTimer() }}
        onTouchMove={() => { startHideControlsTimer() }}
        onClick={() => {
            if (paused) return
            if (showControls)
                setShowControls(false)
            else
                startHideControlsTimer()
        }}
    >
        <Video
            ref={videoControls}
            requestSource={requestSource}
            startTime={startTime}
            resolutionWidth={resolutionWidth}
            audioSource={audioSource}
            subtitleSource={subtitleSource}
            subtitleLinePosition={(showControls || paused) ? -4 : undefined}
            subtitleOffset={subtitleOffset}
            onTimeUpdate={(time) => {
                if (onTimeUpdate) onTimeUpdate(time, requestSource.source.duration)
                setTime(time)
                if (showControls && !hideControlsTimer.current)
                    startHideControlsTimer()
                if (loading)
                    setLoading(false)
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
            <PlayButton aria-label="back" icon={<FaTimes />} onClick={() => {onClose && onClose()}} />
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
                <PlayButton aria-label="Play or pause" icon={paused ? <FaPlay /> : <FaPause />} onClick={() => videoControls.current.togglePlay()} />
                <PlayButton aria-label="Rewind 15 seconds" icon={<FaUndo />} onClick={() => videoControls.current.setCurrentTime(time - 15)} />
                <PlayButton aria-label="Forward 15 seconds" icon={<FaRedo />} onClick={() => videoControls.current.setCurrentTime(time + 15)} />
                <VolumeButton videoControls={videoControls.current} />

                <Flex style={{ marginLeft: 'auto' }} gap="0.5rem">
                    {playNext && <PlayNext {...playNext} />}
                    <SettingsButton
                        playServers={playServers}
                        requestSource={requestSource}
                        resolutionWidth={resolutionWidth}
                        audioSource={audioSource}
                        subtitleSource={subtitleSource}
                        subtitleOffset={subtitleOffset}
                        onRequestSourceChange={setRequestSource}
                        onResolutionWidthChange={setResolutionWidth}
                        onAudioSourceChange={(source) => {
                            setAudioSource(source)
                            if (onAudioChange) onAudioChange(source)
                        }}
                        onSubtitleSourceChange={(source) => {
                            setSubtitleSource(source)
                            if (onSubtitleChange) onSubtitleChange(source)
                        }}
                        onSubtitleOffsetChange={setSubtitleOffset}
                    />
                    <FullscreenButton />
                </Flex>
            </Flex>
        </ControlsBottom>}
    </Box>
}


function FullscreenButton() {
    const [fullscreen, setFullscreen] = useState(false)
    return <>{fullscreen ?
        <PlayButton aria-label="Open fullscreen" icon={<FaExpand />} onClick={() => fullscreenToggle(document.body, setFullscreen)} /> :
        <PlayButton aria-label="Exit fullscreen" icon={<FaArrowsAlt />} onClick={() => fullscreenToggle(document.body, setFullscreen)} />
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


export function SettingsButton(props: ISettingsProps) {
    const { isOpen, onOpen, onClose } = useDisclosure()
    return <>
        <PlayButton aria-label="Settings" onClick={onOpen} icon={<FaCog />} />

        <Modal isOpen={isOpen} onClose={onClose} isCentered scrollBehavior="inside">
            <ModalOverlay />
            <ModalContent layerStyle="baseModal">
                <ModalCloseButton />
                <ModalBody>
                    <Settings {...props} />
                </ModalBody>
            </ModalContent>
        </Modal>
    </>
}


function PlayNext({ title, url }: IPlayNextProps) {
    return <Link to={url} title={title}>
        <PlayButton aria-label={`Play ${title}`} icon={<FaStepForward />} />
    </Link>
}


export const PlayButton = forwardRef<IconButtonProps, 'button'>((props, ref) => {
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
        height="100vh"
        width="100vw"
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