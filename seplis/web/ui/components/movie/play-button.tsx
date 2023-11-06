import api from '@seplis/api'
import { v4 as uuidv4 } from 'uuid'
import { IMovie } from '@seplis/interfaces/movie'
import { IPlayRequest, IPlayServerRequestSource } from '@seplis/interfaces/play-server'
import { IToken } from '@seplis/interfaces/token'
import { useNavigate } from 'react-router-dom'
import { getPlayServers } from '../player/request-play-servers'
import { pickStartSource } from '../player/pick-source'
import { useCast, useCastPlayer } from '../player/react-cast-sender'
import { pickStartSubtitle } from '../player/pick-subtitle-source'
import { pickStartAudio } from '../player/pick-audio-source'
import { getDefaultTrackStyling } from '../player/react-cast-sender/utils/utils'
import { PlayButton } from '../play-button'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'


export default function MoviePlayButton({ movieId }: { movieId: number }) {    
    const { isInitialLoading, data } = useQuery(['movie', 'play-button', movieId], async () => {
    const result = await api.get<IPlayRequest[]>(`/2/movies/${movieId}/play-servers`)
        return result.data.length > 0
    }, {
        enabled: isAuthed()
    })
    const navigate = useNavigate()
    const { connected } = useCast()
    const { loadMedia } = useCastPlayer()

    return data && <PlayButton        
        isLoading={isInitialLoading}
        playServersUrl={`/2/movies/${movieId}/play-servers`}
        onPlayClick={async () => {
            if (connected) {
                const r = await castMovieRequest(movieId)
                await loadMedia(r)            
            } else
                navigate(`/movies/${movieId}/play`)
        }}
    />
}


export function castMovieRequest(
    movieId: number, 
    startTime?: number, 
    requestSource?: IPlayServerRequestSource, 
    audioLang?: string, 
    subtitleLang?: string, 
    subtitleOffset?: number,
    resolutionWidth?: number) {
    return new Promise<chrome.cast.media.LoadRequest>((resolve, reject) => {
        Promise.all([
            getPlayServers(`/2/movies/${movieId}/play-servers`),
            api.post<IToken>('/2/progress-token'),
            api.get<IMovie>(`/2/movies/${movieId}?expand=user_watched`),
        ]).then(result => {
            const session = uuidv4()
            if (!startTime) {
                if (result[2].data)
                    startTime = result[2].data.user_watched?.position
            }

            // for some reason some movies will not start playing if startTime is 0
            if (!startTime || (startTime == 0))
                startTime = 20
                
            if (!requestSource)
                requestSource = pickStartSource(result[0])

            if (!audioLang) {
                const audio = pickStartAudio(requestSource.source.subtitles)
                if (audio)
                    audioLang = `${audio.language}:${audio.index}`
            }

            if (!subtitleLang) {
                const sub = pickStartSubtitle(requestSource.source.subtitles)
                if (sub)
                    subtitleLang = `${sub.language}:${sub.index}`
            }

            const customData = {
                session: session,
                selectedRequestSource: requestSource,
                requestSources: result[0],
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
                resolutionWidth: resolutionWidth,
            }
            const playUrl = customData.selectedRequestSource.request.play_url + `/files/${session}/transcode` +
                `?play_id=${customData.selectedRequestSource.request.play_id}` +
                `&session=${session}` +
                `&start_time=${Math.round(startTime)}` +
                `&source_index=${customData.selectedRequestSource.source.index}` +
                `&supported_video_codecs=h264` +
                `&transcode_video_codec=h264` +
                `&supported_audio_codecs=aac` +
                `&transcode_audio_codec=aac` +
                `&audio_channels=2` +
                `&format=hls` +
                `&audio_lang=${audioLang || ''}`+
                `&width=${resolutionWidth || ''}`

            const mediaInfo = new chrome.cast.media.MediaInfo(playUrl, 'application/x-mpegURL')            
            // @ts-ignore
            mediaInfo.hlsVideoSegmentFormat = chrome.cast.media.HlsSegmentFormat.FMP4
            mediaInfo.streamType = chrome.cast.media.StreamType.OTHER
            mediaInfo.metadata = new chrome.cast.media.MovieMediaMetadata()
            mediaInfo.metadata.title = result[2].data.title
            mediaInfo.metadata.releaseDate = result[2].data.release_date
            mediaInfo.metadata.images = [
                { url: result[2].data.poster_image != null ? result[2].data.poster_image.url + '@SX180.jpg' : '' },
            ]
            mediaInfo.textTrackStyle = getDefaultTrackStyling()
            if (subtitleLang) {
                const track = new chrome.cast.media.Track(1, chrome.cast.media.TrackType.TEXT)
                track.language = subtitleLang
                track.name = subtitleLang
                track.subtype = chrome.cast.media.TextTrackType.CAPTIONS
                track.trackContentType = 'text/vtt'
                track.trackContentId = `${customData.selectedRequestSource.request.play_url}/subtitle-file` +
                    `?play_id=${customData.selectedRequestSource.request.play_id}` +
                    `&start_time=${startTime - (subtitleOffset || 0)}` +
                    `&source_index=${customData.selectedRequestSource.source.index}` +
                    `&lang=${subtitleLang}`
                mediaInfo.tracks = [track]
            }
            const request = new chrome.cast.media.LoadRequest(mediaInfo)
            if (subtitleLang)
                request.activeTrackIds = [1]
            request.customData = customData
            resolve(request)
        }).catch(e => {
            reject(e)
        })
    })
}