import { Box, Flex } from '@chakra-ui/react'
import { IPlayRequest } from '@seplis/interfaces/play-server'
import { secondsToTime } from '@seplis/utils'
import { ReactNode, useState } from 'react'


interface IProps {
    duration: number
    currentTime: number
    onTimeChange: (newTime: number) => void
    playRequest: IPlayRequest
}

export default function Slider({ duration, currentTime, onTimeChange, playRequest }: IProps) {
    const [hoverTime, setHoverTime] = useState<number>(null)

    return <Flex
        cursor="pointer"
        position="relative"
        userSelect="none"
        height="42px"
        width="100%"
        onMouseMove={(e) => hoverMove(e, duration, setHoverTime)}
        onTouchMove={(e) => hoverMove(e, duration, setHoverTime)}
        onMouseLeave={() => setHoverTime(null)}
        onTouchCancel={() => setHoverTime(null)}
        onTouchEnd={() => {
            onTimeChange(hoverTime)
            setHoverTime(null)
        }}
        onClick={() => {
            onTimeChange(hoverTime)
            setHoverTime(null)
        }}
    >
        {hoverTime !== null && <SliderHoverTime time={hoverTime} position={percentage(hoverTime, duration)} />}
        <SliderTrack>
            <SliderTrackProgress progress={percentage(currentTime, duration)} />
        </SliderTrack>
    </Flex>
}


function SliderTrack({ children }: { children: ReactNode }) {
    return <Box
        width="100%"
        top="50%"
        marginTop="-2.5px"
        height="5px"
        backgroundColor="#2E2E2E"
        pointerEvents="none"
        userSelect="none"
        position="relative"
    >
        {children}
    </Box>
}

function SliderTrackProgress({ progress }: { progress: number }) {
    return <Box
        display="block"
        position="absolute"
        height="5px"
        backgroundColor="#428bca"
        userSelect="none"
        style={{ width: `${progress}%` }}
    >

    </Box>
}


function SliderHoverTime({ time, position }: { time: number, position: number }) {
    return <Box
        position="absolute"
        userSelect="none"
        bottom="2.5rem"
        pointerEvents="none"
        textAlign="center"
        padding="0.1rem"
        backgroundColor="#000"
        transform="translate(-50%, 0)"
        style={{ left: `${position}%` }}
    >
        {secondsToTime(time)}
    </Box>
}


function hoverMove(event: any, duration: number, setHoverTime: (time: number) => void) {
    if (event.type.match('^touch')) {
        if (event.originalEvent)
            event = event.originalEvent
        event = event.touches[0] || event.changedTouches[0]
    }
    const r = event.target.getBoundingClientRect()
    const x = event.clientX - r.left
    const norm = duration / (r.right - r.left)
    let time = Math.trunc(norm * x)
    if (time > duration)
        time = duration
    setHoverTime(time)
}


function percentage(currentTime: number, duration: number) {
    const p = (currentTime / duration) * 100
    return p > 100 ? 100 : p
}