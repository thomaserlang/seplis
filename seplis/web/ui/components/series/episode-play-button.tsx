import { Box, Button } from '@chakra-ui/react'
import api from '@seplis/api'
import { IPlayServerRequestSource } from '@seplis/interfaces/play-server'
import { FaPlay } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import { useCast, useCastPlayer } from '../player/react-cast-sender'
import { getPlayServers } from '../player/request-play-servers'
import { v4 as uuidv4 } from 'uuid'
import { IToken } from '@seplis/interfaces/token'
import { ISeries, ISeriesUserSettings } from '@seplis/interfaces/series'
import { IEpisode } from '@seplis/interfaces/episode'
import { pickStartSource } from '../player/pick-source'
import { pickStartAudio } from '../player/pick-audio-source'
import { pickStartSubtitle } from '../player/pick-subtitle-source'
import { getDefaultTrackStyling } from '../player/react-cast-sender/utils/utils'


export function PlayButton({ seriesId, episodeNumber, canPlay }: { seriesId: number, episodeNumber: number, canPlay: boolean }) {
    const navigate = useNavigate()
    const { connected } = useCast()
    const { loadMedia } = useCastPlayer()
    if (!canPlay)
        return null
    return <Box>
        <Button
            leftIcon={<FaPlay />}
            onClick={async () => {
                if (connected) {
                    const r = await castEpisodeRequest(seriesId, episodeNumber)
                    await loadMedia(r)
                } else
                    navigate(`/series/${seriesId}/episodes/${episodeNumber}/play`)
            }}
        >
            Play
        </Button>
    </Box>
}

export function castEpisodeRequest(
    seriesId: number, 
    episodeNumber: number, 
    startTime?: number, 
    requestSource?: IPlayServerRequestSource, 
    audioLang?: string, 
    subtitleLang?: string, 
    subtitleOffset?: number,
    resolutionWidth?: number) {
    return new Promise<chrome.cast.media.LoadRequest>((resolve, reject) => {
        Promise.all([
            getPlayServers(`/2/series/${seriesId}/episodes/${episodeNumber}/play-servers`),
            api.post<IToken>('/2/progress-token'),
            api.get<ISeries>(`/2/series/${seriesId}`),
            api.get<IEpisode>(`/2/series/${seriesId}/episodes/${episodeNumber}?expand=user_watched`),
            api.get<ISeriesUserSettings>(`/2/series/${seriesId}/user-settings`),
        ]).then(result => {
            const session = uuidv4()

            if (!startTime)
                startTime = result[3].data.user_watched?.position

            // for some reason some episodes will not start playing if startTime is 0
            if (!startTime || (startTime == 0))
                startTime = 1    

            if (!requestSource)
                requestSource = pickStartSource(result[0])

            if (!audioLang) {
                const audio = pickStartAudio(requestSource.source.audio, result[4].data?.audio_lang)
                if (audio)
                    audioLang = `${audio.language}:${audio.index}`
            }

            if (!subtitleLang) {
                const sub = pickStartSubtitle(requestSource.source.subtitles, result[4].data?.subtitle_lang)
                if (sub)
                    subtitleLang = `${sub.language}:${sub.index}`
            }

            const customData = {
                session: session,
                selectedRequestSource: requestSource || pickStartSource(result[0], 1920),
                requestSources: result[0],
                token: result[1].data['access_token'],
                type: 'episode',
                series: {
                    id: result[2].data['id'],
                    title: result[2].data['title'],
                    episode_type: result[2].data['episode_type'],
                },
                episode: {
                    number: result[3].data['number'],
                    title: result[3].data['title'],
                    season: result[3].data['season'],
                    episode: result[3].data['episode'],
                },
                startTime: startTime,
                audioLang: audioLang,
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
                `&format=hls`+
                `&audio_lang=${audioLang || ''}`+
                `&width=${resolutionWidth || ''}`
            const mediaInfo = new chrome.cast.media.MediaInfo(playUrl, 'application/x-mpegURL')
            // @ts-ignore
            mediaInfo.hlsVideoSegmentFormat = chrome.cast.media.HlsSegmentFormat.FMP4
            mediaInfo.streamType = chrome.cast.media.StreamType.OTHER
            mediaInfo.metadata = new chrome.cast.media.TvShowMediaMetadata()
            mediaInfo.metadata.seriesTitle = result[2].data.title
            mediaInfo.metadata.title = result[3].data.title
            mediaInfo.metadata.episode = result[3].data.episode || result[3].data.number
            mediaInfo.metadata.season = result[3].data.season
            mediaInfo.metadata.originalAirdate = result[3].data.air_date
            mediaInfo.metadata.metadataType = chrome.cast.media.MetadataType.TV_SHOW
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