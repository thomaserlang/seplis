// @ts-nocheck
import api from '../../api'
import { guid } from '../../utils'
import { getPlayServers } from './request-play-servers'
import { pickStartSource } from './pick-source'


var events = {
    ANY_CHANGED: 'anyChanged',
    AVAILABLE: 'isAvailable',
    IS_CONNECTED: 'isConnected',
    PLAYER_STATE: 'playerState',
    CURRENT_TIME: 'currentTime',
}

class Chromecast {

    constructor() {
        this.loaded = false
    }

    load(onInit?) {
        this.onInit = onInit
        if (!Chromecast.initialized) {
            this.loadCastScript()
        } else {
            this.initCast(true)
        }
    }

    loadCastScript() {
        Chromecast.initList.push(this)
        if (Chromecast.loaded)
            return
        Chromecast.loaded = true
        window['__onGCastApiAvailable'] = (isAvailable) => {
            // Temp fix for cast not reconnecting randomly
            setTimeout(() => {
                let sessionRequest = new chrome.cast.SessionRequest(
                    seplisChromecastAppId
                )
                let apiConfig = new chrome.cast.ApiConfig(
                    sessionRequest,
                    sessionListener,
                    receiverListener,
                    chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
                )
                chrome.cast.initialize(apiConfig, () => {
                    Chromecast.initialized = true
                    for (let obj of Chromecast.initList) {
                        obj.initCast(isAvailable)
                    }
                })
            }, 1000)
        }
        let script = document.createElement('script')
        script.src = 'https://www.gstatic.com/cv/js/sender/v1/cast_sender.js'
        document.head.appendChild(script)
    }

    initCast(isAvailable) {
        this.loaded = isAvailable
        if (!isAvailable)
            return
        if (this.onInit)
            this.onInit(this)
    }

    requestSession() {
        chrome.cast.requestSession(sessionListener)
    }

    isConnected() {
        if (!Chromecast.session)
            return false
        return Chromecast.session.status == 'connected'
    }

    getSession() {
        return Chromecast.session
    }

    getMediaSession() {
        return Chromecast.mediaSession
    }

    getFriendlyName() {
        return Chromecast.session.receiver.friendlyName
    }

    getCurrentTime() {
        return Chromecast.mediaSession.getEstimatedTime()
    }

    playOrPause(success?, error?) {
        if (Chromecast.mediaSession.playerState == 'PLAYING')
            this.pause(success, error)
        else
            this.play(success, error)
    }

    play(success?, error?) {
        Chromecast.mediaSession.play(null, success, error)
    }

    pause(success?, error?) {
        Chromecast.mediaSession.pause(null, success, error)
    }

    playEpisode(seriesId, episodeNumber, startTime?, requestSource?, audioLang?, subtitleLang?, subtitleOffset?) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected()) {
                alert('Not connected to a cast device.')
                reject()
                return
            }
            Promise.all([
                getPlayServers(`/2/series/${seriesId}/episodes/${episodeNumber}/play-servers`),
                api.post('/2/progress-token'),
                api.get(`/2/series/${seriesId}`),
                api.get(`/2/series/${seriesId}/episodes/${episodeNumber}?expand=user_watched`),
                api.get(`/2/series/${seriesId}/user-settings`),
            ]).then(result => {
                const session = guid()
                if (!startTime)
                    startTime = result[3].data.user_watched?.position
                
                if (!audioLang)
                    audioLang = result[4].data?.audio_lang
                if (!subtitleLang)
                    subtitleLang = result[4].data?.subtitle_lang
                
                // for some reason some episodes will not start playing if startTime is 0
                if (!startTime || (startTime == 0))
                    startTime = 1
                const customData = {
                    session: session,
                    selectedRequestSource: requestSource || pickStartSource(result[0]),
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
                }
                let playUrl = customData.selectedRequestSource.request.play_url + `/files/${session}/transcode` +
                    `?play_id=${customData.selectedRequestSource.request.play_id}` +
                    `&session=${session}` +
                    `&start_time=${Math.round(startTime)}` +
                    `&source_index=${customData.selectedRequestSource.source.index}` +
                    `&supported_video_codecs=h264` +
                    `&transcode_video_codec=h264` +
                    `&supported_audio_codecs=aac` +
                    `&transcode_audio_codec=aac` +
                    `&supported_pixel_formats=yuv420p` +
                    `&transcode_pixel_format=yuv420p` +
                    `&audio_channels=2` +
                    `&format=hls`
                if (result[4].data) {
                    playUrl += `&audio_lang=${audioLang || ''}`
                }
                const media = this._playEpisodeMediaInfo(playUrl, result[2].data, result[3].data)
                if (subtitleLang)
                    media.tracks = [this.subtitleTrack(
                        customData.selectedRequestSource.source.index,
                        customData.selectedRequestSource.request,
                        subtitleLang,
                        startTime,
                        subtitleOffset
                    )]
                const request = new chrome.cast.media.LoadRequest(media)
                request.customData = customData
                if (subtitleLang)
                    request.activeTrackIds = [1]
                this.getSession().loadMedia(
                    request,
                    mediaSession => {
                        mediaListener(mediaSession)
                        const srequest = new chrome.cast.media.SeekRequest()
                        srequest.currentTime = 1
                        mediaSession.seek(srequest, (success) => {
                        }, (error) => {
                            console.log(error)
                        })
                        resolve(mediaSession)
                    },
                    e => {
                        console.log(e)
                        reject(e)
                    }, Chromecast
                )
            }).catch(e => {
                reject(e)
            })
        })
    }

    seek(time: number) {
        const r = new chrome.cast.media.SeekRequest()
        r.currentTime = time
        Chromecast.mediaSession.seek(r)
    }

    requestCustomData() {
        Chromecast.session.sendMessage(
            'urn:x-cast:net.seplis.cast.get_custom_data', 
            {}
        )
    }

    playMovie(movieId, startTime?, requestSource?, audioLang?, subtitleLang?, subtitleOffset?) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected()) {
                alert('Not connected to a cast device.')
                reject()
                return
            }
            Promise.all([
                getPlayServers(`/2/movies/${movieId}/play-servers`),
                api.post('/2/progress-token'),
                api.get(`/2/movies/${movieId}?expand=user_watched`),
            ]).then(result => {
                if (!startTime) {
                    if (result[2].data)
                        startTime = result[2].data.user_watched?.position
                }
                // for some reason some movies will not start playing if startTime is 0
                if (!startTime || (startTime == 0))
                    startTime = 10
                const session = guid()
                const customData = {
                    session: session,
                    selectedRequestSource: requestSource || pickStartSource(result[0]),
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
                    `&supported_pixel_formats=yuv420p` +
                    `&transcode_pixel_format=yuv420p` +
                    `&audio_channels=2` +
                    `&format=hls` +
                    `&audio_lang=${audioLang || ''}`

                const media = this._playMovieMediaInfo(playUrl, result[2].data)
                if (subtitleLang)
                    media.tracks = [this.subtitleTrack(
                        customData.selectedRequestSource.source.index,
                        customData.selectedRequestSource.request,
                        subtitleLang,
                        startTime,
                        subtitleOffset,
                    )]
                const request = new chrome.cast.media.LoadRequest(media)
                request.customData = customData
                if (subtitleLang)
                    request.activeTrackIds = [1]
                this.getSession().loadMedia(
                    request,
                    mediaSession => {
                        mediaListener(mediaSession)
                        resolve(mediaSession)
                    },
                    e => {
                        reject(e)
                    }, Chromecast
                )
            }).catch(e => {
                reject(e)
            })
        })
    }

    subtitleTrack(source_index, playServer, subtitle_lang, startTime, offset) {
        const track = new chrome.cast.media.Track(1, chrome.cast.media.TrackType.TEXT)
        track.language = subtitle_lang
        track.name = subtitle_lang
        track.subtype = chrome.cast.media.TextTrackType.CAPTIONS
        track.trackContentType = 'text/vtt'
        track.trackContentId = `${playServer.play_url}/subtitle-file` +
            `?play_id=${playServer.play_id}` +
            `&start_time=${(startTime || 0) - (offset || 0)}` +
            `&source_index=${source_index}` +
            `&lang=${subtitle_lang}`
        return track
    }


    _playEpisodeMediaInfo(url, show, episode) {
        const mediaInfo = new chrome.cast.media.MediaInfo(url)
        mediaInfo.contentType = 'application/x-mpegURL'
        mediaInfo.hlsVideoSegmentFormat = chrome.cast.media.HlsSegmentFormat.FMP4
        mediaInfo.streamType = chrome.cast.media.StreamType.OTHER
        mediaInfo.metadata = new chrome.cast.media.TvShowMediaMetadata()
        mediaInfo.metadata.seriesTitle = show.title
        mediaInfo.metadata.title = episode.title
        mediaInfo.metadata.episode = episode.episode || episode.number
        mediaInfo.metadata.season = episode.season
        mediaInfo.metadata.originalAirdate = episode.air_date
        mediaInfo.metadata.metadataType = chrome.cast.media.MetadataType.TV_SHOW
        mediaInfo.metadata.images = [
            { url: show.poster_image != null ? show.poster_image.url + '@SX180.jpg' : '' },
        ]
        mediaInfo.textTrackStyle = new chrome.cast.media.TextTrackStyle();
        mediaInfo.textTrackStyle.fontFamily = 'CASUAL';
        mediaInfo.textTrackStyle.fontScale = 1.0;
        return mediaInfo
    }

    _playMovieMediaInfo(url, movie) {
        const mediaInfo = new chrome.cast.media.MediaInfo(url)
        mediaInfo.contentType = 'application/x-mpegURL';
        mediaInfo.hlsVideoSegmentFormat = chrome.cast.media.HlsSegmentFormat.FMP4;
        mediaInfo.streamType = chrome.cast.media.StreamType.OTHER
        mediaInfo.metadata = new chrome.cast.media.MovieMediaMetadata()
        mediaInfo.metadata.title = movie.title
        mediaInfo.metadata.releaseDate = movie.release_date
        mediaInfo.metadata.images = [
            { url: movie.poster_image != null ? movie.poster_image.url + '@SX180.jpg' : '' },
        ]
        mediaInfo.textTrackStyle = new chrome.cast.media.TextTrackStyle();
        mediaInfo.textTrackStyle.fontFamily = 'CASUAL';
        mediaInfo.textTrackStyle.fontScale = 1.0;
        return mediaInfo
    }

    addEventListener(event, func) {
        if (!(event in Chromecast.eventListener))
            Chromecast.eventListener[event] = []
        let e = Chromecast.eventListener[event]
        if (!Chromecast.eventListener[event].includes(func))
            Chromecast.eventListener[event].push(func)
    }

    removeEventListener(event, func) {
        const e = Chromecast.eventListener[event] || []
        const i = e.indexOf(func)
        if (i > -1)
            e.splice(i, 1)
    }
}
Chromecast.initialized = false
Chromecast.loaded = false
Chromecast.initList = []
Chromecast.session = null
Chromecast.mediaSession = null
Chromecast.eventListener = {}
Chromecast.events = events
Chromecast.timerGetCurrentTime = null

function sessionListener(session) {
    Chromecast.session = session
    if (session.media.length != 0) {
        mediaListener(session.media[0])
    }
    Chromecast.timerGetCurrentTime = setInterval(() => {
        if (!Chromecast.mediaSession)
            return
        if (Chromecast.mediaSession.playerState == 'PLAYING')
            dispatchEvent(events.CURRENT_TIME, Chromecast.mediaSession.getEstimatedTime())
    }, 1000)
    session.addMediaListener(mediaListener)
    session.addUpdateListener(sessionUpdateListener)
    dispatchEvent(events.IS_CONNECTED, true)
}

function sessionUpdateListener(event) {
    if (Chromecast.session.status !== chrome.cast.SessionStatus.CONNECTED) {
        Chromecast.session = null
        Chromecast.mediaSession = null
        dispatchEvent(events.IS_CONNECTED, false)
    }
}

function mediaListener(mediaSession) {
    Chromecast.mediaSession = mediaSession
    mediaSession.addUpdateListener(mediaSessionUpdateListener)
    dispatchEvent(events.CURRENT_TIME, Chromecast.mediaSession.getEstimatedTime())
}

function mediaSessionUpdateListener() {
    dispatchEvent(
        events.PLAYER_STATE,
        Chromecast.mediaSession.playerState
    )
}

function receiverListener(state) {
    if (state == 'available')
        dispatchEvent(events.AVAILABLE, true)
    else
        dispatchEvent(events.AVAILABLE, false)
}

function mediaStatusUpdateListener(isAlive) {

}

function dispatchEvent(event, data) {
    let e = {
        field: event,
        value: data,
    }
    _dispatchEvent('anyChanged', e)
    _dispatchEvent(event, e)
}

function _dispatchEvent(event, data) {
    let e = Chromecast.eventListener[event] || []
    e.forEach(f => {
        try {
            f(data)
        } catch (e) {
            console.log(e)
        }
    })
}

export default Chromecast