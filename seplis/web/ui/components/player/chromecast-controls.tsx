import { Box, Flex } from '@chakra-ui/react'
import api from '@seplis/api'
import { episodeTitle, secondsToTime } from '@seplis/utils'
import { useEffect, useState } from 'react'
import { FaPause, FaPlay } from 'react-icons/fa'
import { useLocalStorage } from 'usehooks-ts'
import { castMovieRequest } from '../movie/play-button'
import { castEpisodeRequest } from '../series/episode-play-button'
import { pickStartAudio } from './pick-audio-source'
import { MAX_BITRATE } from './pick-quality'
import { pickStartSubtitle } from './pick-subtitle-source'
import { PlayButton } from './player'
import { useCast, useCastPlayer } from './react-cast-sender'
import { SettingsMenu } from './settings'
import Slider from './slider'

export default function ChromecastControls() {
    const { connected } = useCast()
    const {
        currentTime,
        togglePlay,
        isPaused,
        sendMessage,
        loadMedia,
        seek,
        isMediaLoaded,
    } = useCastPlayer()
    const [info, setInfo] = useState<any>()
    const [maxBitrate, setMaxBitrate] = useLocalStorage(
        'seplis:cast:maxBitrate',
        MAX_BITRATE
    )

    useEffect(() => {
        try {
            const castSession =
                window.cast.framework.CastContext.getInstance().getCurrentSession()
            if (castSession) {
                castSession.addMessageListener(
                    'urn:x-cast:net.seplis.cast.get_custom_data',
                    infoReceived
                )
            }
            return () => {
                if (castSession) {
                    castSession.removeMessageListener(
                        'urn:x-cast:net.seplis.cast.get_custom_data',
                        infoReceived
                    )
                }
            }
        } catch {}
    }, [connected])

    const infoReceived = (namespace: string, message: any) => {
        if (message) setInfo(JSON.parse(message))
    }

    if (!info) return

    return (
        <Box background="blackAlpha.500" padding="0.5rem" rounded="md">
            {isMediaLoaded && currentTime > 0 && (
                <Flex gap="0.5rem" align="center">
                    <Box fontSize="14px">{secondsToTime(currentTime)}</Box>
                    <Flex grow="1">
                        <Slider
                            duration={
                                info.selectedRequestSource.source.duration
                            }
                            currentTime={currentTime}
                            playRequest={info.selectedRequestSource.request}
                            onTimeChange={async (time) => {
                                seek(time)
                            }}
                        />
                    </Flex>
                    <Box fontSize="14px">
                        {secondsToTime(
                            info.selectedRequestSource.source.duration
                        )}
                    </Box>
                </Flex>
            )}
            <Flex gap="1rem" alignItems="center">
                <PlayButton
                    aria-label="Play or pause"
                    icon={isPaused ? <FaPlay /> : <FaPause />}
                    onClick={() => togglePlay()}
                />

                <Box>
                    {info.type == 'episode'
                        ? `${info.series.title} ${episodeTitle(info.episode)}`
                        : info.movie.title}
                </Box>

                <Flex style={{ marginLeft: 'auto' }} gap="0.5rem">
                    <SettingsMenu
                        playServers={info.requestSources}
                        requestSource={info.selectedRequestSource}
                        maxBitrate={info.maxBitrate}
                        audioSource={pickStartAudio(
                            info.selectedRequestSource.source.audio,
                            info.audioLang
                        )}
                        subtitleSource={pickStartSubtitle(
                            info.selectedRequestSource.source.subtitles,
                            info.subtitleLang
                        )}
                        subtitleOffset={info.subtitleOffset}
                        onRequestSourceChange={async (source) => {
                            if (info.type == 'episode')
                                loadMedia(
                                    await castEpisodeRequest({
                                        seriesId: info.series.id,
                                        episodeNumber: info.episode.number,
                                        startTime: currentTime,
                                        requestSource: source,
                                        audioLang: info.audioLang,
                                        subtitleLang: info.subtitleLang,
                                        subtitleOffset: info.subtitleOffset,
                                        maxBitrate: maxBitrate,
                                    })
                                )
                            else if (info.type == 'movie')
                                loadMedia(
                                    await castMovieRequest({
                                        movieId: info.movie.id,
                                        startTime: currentTime,
                                        requestSource: source,
                                        audioLang: info.audioLang,
                                        subtitleLang: info.subtitleLang,
                                        subtitleOffset: info.subtitleOffset,
                                        maxBitrate: maxBitrate,
                                    })
                                )
                        }}
                        onMaxBitrateChange={async (maxBitrate) => {
                            setMaxBitrate(maxBitrate)
                            if (info.type == 'episode')
                                loadMedia(
                                    await castEpisodeRequest({
                                        seriesId: info.series.id,
                                        episodeNumber: info.episode.number,
                                        startTime: currentTime,
                                        requestSource:
                                            info.selectedRequestSource,
                                        audioLang: info.audioLang,
                                        subtitleLang: info.subtitleLang,
                                        subtitleOffset: info.subtitleOffset,
                                        maxBitrate: maxBitrate,
                                    })
                                )
                            else if (info.type == 'movie')
                                loadMedia(
                                    await castMovieRequest({
                                        movieId: info.movie.id,
                                        startTime: currentTime,
                                        requestSource:
                                            info.selectedRequestSource,
                                        audioLang: info.audioLang,
                                        subtitleLang: info.subtitleLang,
                                        subtitleOffset: info.subtitleOffset,
                                        maxBitrate,
                                    })
                                )
                        }}
                        onAudioSourceChange={async (source) => {
                            if (info.type == 'episode') {
                                api.put(
                                    `/2/series/${info.series.id}/user-settings`,
                                    {
                                        audio_lang: source
                                            ? `${
                                                  source.language ||
                                                  source.title
                                              }:${source.index}`
                                            : null,
                                    }
                                )
                                loadMedia(
                                    await castEpisodeRequest({
                                        seriesId: info.series.id,
                                        episodeNumber: info.episode.number,
                                        startTime: currentTime,
                                        requestSource:
                                            info.selectedRequestSource,
                                        audioLang: source
                                            ? `${source.language}:${source.index}`
                                            : null,
                                        subtitleLang: info.subtitleLang,
                                        subtitleOffset: info.subtitleOffset,
                                        maxBitrate: info.maxBitrate,
                                    })
                                )
                            } else if (info.type == 'movie')
                                loadMedia(
                                    await castMovieRequest({
                                        movieId: info.movie.id,
                                        startTime: currentTime,
                                        requestSource:
                                            info.selectedRequestSource,
                                        audioLang: source
                                            ? `${source.language}:${source.index}`
                                            : null,
                                        subtitleLang: info.subtitleLang,
                                        subtitleOffset: info.subtitleOffset,
                                        maxBitrate: info.maxBitrate,
                                    })
                                )
                        }}
                        onSubtitleSourceChange={(source) => {
                            let url = ''
                            let lang = ''
                            if (info.type === 'episode')
                                api.put(
                                    `/2/series/${info.series.id}/user-settings`,
                                    {
                                        subtitle_lang: source
                                            ? `${
                                                  source.language ||
                                                  source.title
                                              }:${source.index}`
                                            : 'off',
                                    }
                                )
                            if (source) {
                                lang = `${source.language}:${source.index}`
                                url =
                                    `${info.selectedRequestSource.request.play_url}/subtitle-file` +
                                    `?play_id=${info.selectedRequestSource.request.play_id}` +
                                    `&source_index=${info.selectedRequestSource.source.index}` +
                                    `&lang=${lang}`
                                if (info.subtitleOffset)
                                    url = url + `&offset=${info.subtitleOffset}`
                            }
                            sendMessage(
                                'urn:x-cast:net.seplis.cast.new_track',
                                {
                                    url: url,
                                    lang: lang,
                                    offset: info.subtitleOffset,
                                }
                            )
                            setInfo({
                                ...info,
                                subtitleLang: lang,
                            })
                        }}
                        onSubtitleOffsetChange={(offset) => {
                            if (info.subtitleLang) {
                                let url =
                                    `${info.selectedRequestSource.request.play_url}/subtitle-file` +
                                    `?play_id=${info.selectedRequestSource.request.play_id}` +
                                    `&source_index=${info.selectedRequestSource.source.index}` +
                                    `&lang=${info.subtitleLang}`
                                if (offset) url = url + `&offset=${offset}`
                                sendMessage(
                                    'urn:x-cast:net.seplis.cast.new_track',
                                    {
                                        url: url,
                                        lang: info.subtitleLang,
                                        offset: offset,
                                    }
                                )
                                setInfo({
                                    ...info,
                                    subtitleOffset: offset,
                                })
                            }
                        }}
                    />
                </Flex>
            </Flex>
        </Box>
    )
}
