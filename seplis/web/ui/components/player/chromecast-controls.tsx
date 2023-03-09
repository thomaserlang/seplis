import { Box, Flex } from '@chakra-ui/react'
import { episodeTitle, secondsToTime } from '@seplis/utils'
import { useCallback, useEffect, useRef, useState } from 'react'
import { FaPause, FaPlay, FaRedo, FaUndo } from 'react-icons/fa'
import Chromecast from './Chromecast'
import { pickStartAudio } from './pick-audio-source'
import { pickStartSubtitle } from './pick-subtitle-source'
import { PlayButton, SettingsButton } from './player'
import Slider from './slider'


export default function ChromecastControls() {
    const cast = useRef<Chromecast>()
    const [connected, setConnected] = useState(false)
    const [info, setInfo] = useState<any>()
    const [time, setTime] = useState(0)
    const [playing, setPlaying] = useState(false)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (cast) {
            cast.current = new Chromecast()
            cast.current.load()
        }

        const stateChange = (event: any) => {
            switch (event.field) {
                case 'playerState':
                    setPlaying(event.value == 'PLAYING')
                    setLoading(event.value !== 'PLAYING' && event.value !== 'PAUSED')
                    setConnected(cast.current.isConnected())
                    cast.current.requestCustomData()
                    break
                case 'isConnected':
                    setConnected(cast.current.isConnected())
                    break
                case 'isAvailable':
                    setConnected(cast.current.isConnected())
                    break
                case 'currentTime':
                    setTime(cast.current.getMediaSession()?.liveSeekableRange && info ? event.value + (info?.startTime || 0) : event.value)
                    setPlaying(true)
                    setLoading(false)
                    break
            }
        }

        cast.current.addEventListener('anyChanged', stateChange)

        return () => {
            cast.current.removeEventListener('anyChanged', stateChange)
        }
    }, [info])

    useEffect(() => {
        cast.current.getSession()?.addMessageListener(
            'urn:x-cast:net.seplis.cast.get_custom_data',
            infoReceived,
        )
        return () => {
            cast.current.getSession()?.removeMessageListener(
                'urn:x-cast:net.seplis.cast.get_custom_data',
                infoReceived
            )
        }
    }, [connected])

    const infoReceived = (namespace: string, message: any) => {
        if (message)
            setInfo(JSON.parse(message))
    }

    if (!info)
        return

    return <Box background="blackAlpha.500" padding="0.5rem" rounded="md">
        <Flex gap="0.5rem" align="center">
            <Box fontSize="14px">{secondsToTime(time)}</Box>
            <Flex grow="1">
                <Slider
                    duration={info.selectedRequestSource.source.duration}
                    currentTime={time}
                    playRequest={info.selectedRequestSource.request}
                    onTimeChange={(time) => {
                        cast.current.pause()
                        if (info.type == 'episode')
                            cast.current.playEpisode(info.series.id, info.episode.number, time, info.selectedRequestSource, info.audioLang, info.subtitleLang, info.subtitleOffset)
                        else if (info.type == 'movie')
                            cast.current.playMovie(info.movie.id, time, info.selectedRequestSource, info.audioLang, info.subtitleLang, info.subtitleOffset)
                        setTime(time)
                    }}
                />
            </Flex>
            <Box fontSize="14px">{secondsToTime(info.selectedRequestSource.source.duration)}</Box>
        </Flex>
        <Flex gap="1rem" alignItems="center">
            <PlayButton isLoading={loading} aria-label="Play or pause" icon={!playing ? <FaPlay /> : <FaPause />} onClick={() => cast.current.playOrPause()} />

            <Box>{info.type == 'episode' ? `${info.series.title} ${episodeTitle(info.episode)}` : info.movie.title}</Box>

            <Flex style={{ marginLeft: 'auto' }} gap="0.5rem">

                <SettingsButton
                    playServers={info.requestSources}
                    requestSource={info.selectedRequestSource}
                    //resolutionWidth={resolutionWidth}
                    audioSource={pickStartAudio(info.selectedRequestSource, info.audioLang)}
                    subtitleSource={pickStartSubtitle(info.selectedRequestSource, info.subtitleLang)}
                    subtitleOffset={info.subtitleOffset}
                    onRequestSourceChange={(s) => {
                        if (info.type == 'episode')
                            cast.current.playEpisode(info.series.id, info.episode.number, time, s, info.audioLang, info.subtitleLang, info.subtitleOffset)
                        else if (info.type == 'movie')
                            cast.current.playMovie(info.movie.id, time, s, info.audioLang, info.subtitleLang, info.subtitleOffset)
                    }}
                    //onResolutionWidthChange={setResolutionWidth}
                    onAudioSourceChange={(source) => {
                        if (info.type == 'episode')
                            cast.current.playEpisode(info.series.id, info.episode.number, time, info.selectedRequestSource, `${source.language}:${source.index}`, info.subtitleLang, info.subtitleOffset)
                        else if (info.type == 'movie')
                            cast.current.playMovie(info.movie.id, time, info.selectedRequestSource, `${source.language}:${source.index}`, info.subtitleLang, info.subtitleOffset)
                    }}
                    onSubtitleSourceChange={(source) => {
                        if (info.type == 'episode')
                            cast.current.playEpisode(info.series.id, info.episode.number, time, info.selectedRequestSource, info.audioLang, source ? `${source.language}:${source.index}` : null, info.subtitleOffset)
                        else if (info.type == 'movie')
                            cast.current.playMovie(info.movie.id, time, info.selectedRequestSource, info.audioLang, source ? `${source.language}:${source.index}` : null, info.subtitleOffset)
                    }}
                    onSubtitleOffsetChange={(offset) => {
                        if (info.type == 'episode')
                            cast.current.playEpisode(info.series.id, info.episode.number, time, info.selectedRequestSource, info.audioLang, info.subtitleLang, offset)
                        else if (info.type == 'movie')
                            cast.current.playMovie(info.movie.id, time, info.selectedRequestSource, info.audioLang, info.subtitleLang, offset)
                    }}
                />
            </Flex>
        </Flex>
    </Box>
}