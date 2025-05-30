import api from '@seplis/api'
import { IMovie } from '@seplis/interfaces/movie'
import {
    IPlayRequest,
    IPlayServerRequestMedia,
    IPlayServerRequestSource,
} from '@seplis/interfaces/play-server'
import { IToken } from '@seplis/interfaces/token'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useLocalStorage } from 'usehooks-ts'
import { v4 as uuidv4 } from 'uuid'
import { PlayButton } from '../play-button'
import { pickStartAudio } from '../player/pick-audio-source'
import { MAX_BITRATE } from '../player/pick-quality'
import { pickStartSource } from '../player/pick-source'
import { pickStartSubtitle } from '../player/pick-subtitle-source'
import { useCast, useCastPlayer } from '../player/react-cast-sender'
import { getDefaultTrackStyling } from '../player/react-cast-sender/utils/utils'
import { getPlayServers } from '../player/request-play-servers'

export default function MoviePlayButton({ movieId }: { movieId: number }) {
    const { isInitialLoading, data } = useQuery(
        ['movie', 'play-button', movieId],
        async () => {
            const result = await api.get<IPlayRequest[]>(
                `/2/movies/${movieId}/play-servers`
            )
            return result.data.length > 0
        },
        {
            enabled: isAuthed(),
        }
    )
    const navigate = useNavigate()
    const { connected } = useCast()
    const { loadMedia } = useCastPlayer()
    const [maxBitrate] = useLocalStorage('seplis:cast:maxBitrate', MAX_BITRATE)

    return (
        data && (
            <PlayButton
                isLoading={isInitialLoading}
                playServersUrl={`/2/movies/${movieId}/play-servers`}
                onPlayClick={async () => {
                    if (connected) {
                        const r = await castMovieRequest({
                            movieId,
                            maxBitrate,
                        })
                        await loadMedia(r)
                    } else navigate(`/movies/${movieId}/play`)
                }}
            />
        )
    )
}

export function castMovieRequest({
    movieId,
    startTime,
    requestSource,
    audioLang,
    subtitleLang,
    subtitleOffset,
    maxBitrate,
}: {
    movieId: number
    startTime?: number
    requestSource?: IPlayServerRequestSource
    audioLang?: string
    subtitleLang?: string
    subtitleOffset?: number
    maxBitrate?: number
}) {
    return new Promise<chrome.cast.media.LoadRequest>((resolve, reject) => {
        Promise.all([
            getPlayServers(`/2/movies/${movieId}/play-servers`),
            api.post<IToken>('/2/progress-token'),
            api.get<IMovie>(`/2/movies/${movieId}?expand=user_watched`),
        ])
            .then(async (result) => {
                const session = uuidv4()
                if (!startTime) {
                    if (result[2].data)
                        startTime = result[2].data.user_watched?.position
                }

                if (!startTime) startTime = 0

                if (!requestSource) requestSource = pickStartSource(result[0])

                if (!audioLang) {
                    const audio = pickStartAudio(requestSource.source.subtitles)
                    if (audio) audioLang = `${audio.language}:${audio.index}`
                }

                if (!subtitleLang) {
                    const sub = pickStartSubtitle(
                        requestSource.source.subtitles
                    )
                    if (sub) subtitleLang = `${sub.language}:${sub.index}`
                }

                const r = await axios.get<IPlayServerRequestMedia>(
                    `${requestSource.request.play_url}/request-media` +
                        `?play_id=${requestSource.request.play_id}` +
                        `&source_index=${requestSource.source.index}` +
                        `&session=${session}` +
                        `&start_time=${startTime}` +
                        `&supported_video_codecs=h264` +
                        `&transcode_video_codec=h264` +
                        `&supported_audio_codecs=aac` +
                        `&transcode_audio_codec=aac` +
                        `&max_audio_channels=2` +
                        `&format=hls` +
                        `&audio_lang=${audioLang || ''}` +
                        `&max_video_bitrate=${maxBitrate || ''}` +
                        `&supported_video_containers=mp4`
                )
                const requestMedia = r.data
                requestMedia.hls_url =
                    requestSource.request.play_url + r.data.hls_url
                requestMedia.direct_play_url =
                    requestSource.request.play_url + r.data.direct_play_url

                const mediaInfo = new chrome.cast.media.MediaInfo(
                    requestMedia.hls_url,
                    'application/x-mpegURL'
                )
                // @ts-ignore
                mediaInfo.hlsVideoSegmentFormat = // @ts-ignore
                    chrome.cast.media.HlsSegmentFormat.FMP4
                mediaInfo.streamType = chrome.cast.media.StreamType.OTHER

                mediaInfo.metadata = new chrome.cast.media.MovieMediaMetadata()
                mediaInfo.metadata.title = result[2].data.title
                mediaInfo.metadata.releaseDate = result[2].data.release_date
                mediaInfo.metadata.images = [
                    {
                        url:
                            result[2].data.poster_image != null
                                ? result[2].data.poster_image.url + '@SX180.jpg'
                                : '',
                    },
                ]
                mediaInfo.textTrackStyle = getDefaultTrackStyling()

                const customData = {
                    session: session,
                    selectedRequestSource: requestSource,
                    requestSources: result[0],
                    requestMedia: requestMedia,
                    token: result[1].data['access_token'],
                    type: 'movie',
                    movie: {
                        id: result[2].data['id'],
                        title: result[2].data['title'],
                    },
                    startTime: startTime,
                    audioLang: audioLang || '',
                    subtitleLang: subtitleLang || '',
                    subtitleOffset: subtitleOffset || 0,
                    apiUrl: (window as any).seplisAPI,
                    maxBitrate: maxBitrate,
                }

                if (subtitleLang) {
                    const track = new chrome.cast.media.Track(
                        1,
                        chrome.cast.media.TrackType.TEXT
                    )
                    track.language = subtitleLang
                    track.name = subtitleLang
                    track.subtype = chrome.cast.media.TextTrackType.CAPTIONS
                    track.trackContentType = 'text/vtt'
                    track.trackContentId =
                        `${customData.selectedRequestSource.request.play_url}/subtitle-file` +
                        `?play_id=${customData.selectedRequestSource.request.play_id}` +
                        `&source_index=${customData.selectedRequestSource.source.index}` +
                        `&lang=${subtitleLang}`
                    if (subtitleOffset)
                        track.trackContentId =
                            track.trackContentId + `&offset=${subtitleOffset}`
                    mediaInfo.tracks = [track]
                }
                const request = new chrome.cast.media.LoadRequest(mediaInfo)
                if (subtitleLang) request.activeTrackIds = [1]
                request.customData = customData
                request.currentTime = startTime
                resolve(request)
            })
            .catch((e) => {
                reject(e)
            })
    })
}
