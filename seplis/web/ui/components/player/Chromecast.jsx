import {getPlayServer} from './Player'
import {request} from 'api'
import {guid} from 'utils'

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

    load(onInit) {
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
            }, 500)
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

    playOrPause(success, error) {
        if (Chromecast.mediaSession.playerState == 'PLAYING')
            this.pause(success, error)
        else
            this.play(success, error)
    }    

    play(success, error) {
        Chromecast.mediaSession.play(null, success, error)
    }

    pause(success, error) {
        Chromecast.mediaSession.pause(null, success, error)
    }

    playEpisode(showId, episodeNumber, startTime) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected()) {
                alert('Not connected to a cast device.')
                reject()
                return
            }
            let url =`/1/shows/${showId}/episodes/${episodeNumber}/play-servers`
            Promise.all([
                getPlayServer(url),
                request('/1/progress-token'),
                request(`/1/shows/${showId}`),
                request(`/1/shows/${showId}/episodes/${episodeNumber}`),
                request(`/1/shows/${showId}/episodes/${episodeNumber}/watched`),
                request(`/1/shows/${showId}/user-subtitle-lang`),
            ]).then(result => {
                const session = guid()
                if (!startTime) {
                    if (result[4])
                        startTime = result[4].position
                    else
                        startTime = 1
                }
                let customData = {
                    session: session,
                    play: result[0]['playServer'],
                    selectedSource: result[0]['sources'][0],
                    sources: result[0]['sources'],
                    token: result[1]['token'],
                    type: 'episode',
                    series: {
                        id: result[2]['id'],
                        title: result[2]['title'],
                        episode_type: result[2]['episode_type'],
                    },
                    episode: {
                        number: result[3]['number'],
                        title: result[3]['title'],
                        season: result[3]['season'],
                        episode: result[3]['episode'],
                    },
                    startTime: startTime,
                    apiUrl: seplisBaseUrl,
                }
                let playUrl = result[0].playServer.play_url+`/files/${session}/transcode`+
                    `?play_id=${result[0].playServer.play_id}`+
                    `&session=${session}`+
                    `&start_time=${startTime}`+
                    `&source_index=${customData.selectedSource.index}`+
                    `&supported_video_codecs=h264`+
                    `&transcode_video_codec=h264`+
                    `&supported_audio_codecs=aac`+
                    `&transcode_audio_codec=aac`+
                    `&supported_pixel_formats=yuv420p`+
                    `&transcode_pixel_format=yuv420p`+
                    `&audio_channels=2`+
                    `&format=hls`
                if (result[5]) {
                    // playUrl += `&subtitle_lang=${result[5].subtitle_lang || ''}`
                    playUrl += `&audio_lang=${result[5].audio_lang || ''}`
                }
                const media = this._playEpisodeMediaInfo(playUrl, result[2], result[3])
                if (result[5].subtitle_lang)
                    media.tracks = [this.subtitleTrack(customData.selectedSource.index, result[0].playServer, result[5].subtitle_lang, startTime)]
                const request = new chrome.cast.media.LoadRequest(media)
                request.customData = customData
                if (result[5].subtitle_lang)
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

    playMovie(movieId, startTime, audioLang, subtitleLang) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected()) {
                alert('Not connected to a cast device.')
                reject()
                return
            }
            let url =`/1/movies/${movieId}/play-servers`
            Promise.all([
                getPlayServer(url),
                request('/1/progress-token'),
                request(`/1/movies/${movieId}`),
                request(`/1/movies/${movieId}/watched`),
            ]).then(result => {
                if (!startTime) {
                    if (result[3])
                        startTime = result[3].position
                    else
                        startTime = 1 // for some reason some movies will not start playing if startTime is 0
                }
                const session = guid()
                const customData = {
                    session: session,
                    play: result[0]['playServer'],
                    selectedSource: result[0]['sources'][0],
                    sources: result[0]['sources'],
                    token: result[1]['token'],
                    type: 'movie',
                    movie: {
                        id: result[2]['id'],
                        title: result[2]['title'],
                    },
                    startTime: startTime,
                    apiUrl: seplisBaseUrl,
                }
                const playUrl = result[0].playServer.play_url+`/files/${session}/transcode`+
                    `?play_id=${result[0].playServer.play_id}`+
                    `&session=${session}`+
                    `&start_time=${startTime}`+
                    `&source_index=${customData.selectedSource.index}`+
                    `&supported_video_codecs=h264`+
                    `&transcode_video_codec=h264`+
                    `&supported_audio_codecs=aac`+
                    `&transcode_audio_codec=aac`+
                    `&supported_pixel_formats=yuv420p`+
                    `&transcode_pixel_format=yuv420p`+
                    `&audio_channels=2`+
                    `&format=hls`+
                    `&audio_lang=${audioLang || ''}`
                
                const media = this._playMovieMediaInfo(playUrl, result[2], result[3])
                if (subtitleLang)
                    media.tracks = [this.subtitleTrack(customData.selectedSource.index, result[0].playServer, subtitleLang, startTime || 1)]
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

    subtitleTrack(source_index, playServer, subtitle_lang, startTime) {
        const track = new chrome.cast.media.Track(1, chrome.cast.media.TrackType.TEXT)
        track.language = subtitle_lang
        track.name = subtitle_lang
        track.subtype = chrome.cast.media.TextTrackType.CAPTIONS
        track.trackContentType = 'text/vtt'
        track.trackContentId = `${playServer.play_url}/subtitle-file`+
            `?play_id=${playServer.play_id}`+
            `&start_time=${startTime || 0}`+
            `&source_index=${source_index}`+
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
            {url:show.poster_image!=null?show.poster_image.url + '@SX180.jpg':''},
        ]
        mediaInfo.textTrackStyle = new chrome.cast.media.TextTrackStyle();
        mediaInfo.textTrackStyle.backgroundColor = '#00000000';
        mediaInfo.textTrackStyle.edgeColor       = '#00000016';
        mediaInfo.textTrackStyle.edgeType        = 'DROP_SHADOW';
        mediaInfo.textTrackStyle.fontFamily      = 'CASUAL';
        mediaInfo.textTrackStyle.fontScale       = 1.0;
        mediaInfo.textTrackStyle.foregroundColor = '#FFFFFF';
        return mediaInfo
    }

    _playMovieMediaInfo(url, movie) {
        const mediaInfo = new chrome.cast.media.MediaInfo(url)
        mediaInfo.contentType = 'application/x-mpegURL';
        mediaInfo.hlsVideoSegmentFormat = chrome.cast.media.HlsSegmentFormat.FMP4;
        mediaInfo.streamType = chrome.cast.media.StreamType.OTHER
        mediaInfo.metadata = new chrome.cast.media.MovieMediaMetadata()
        mediaInfo.metadata.title = movie.title
        mediaInfo.metadata.releaseDate = movie.released
        mediaInfo.metadata.images = [
            {url:movie.poster_image!=null?movie.poster_image.url + '@SX180.jpg':''},
        ]
        mediaInfo.textTrackStyle = new chrome.cast.media.TextTrackStyle();
        mediaInfo.textTrackStyle.backgroundColor = '#00000000';
        mediaInfo.textTrackStyle.edgeColor       = '#00000016';
        mediaInfo.textTrackStyle.edgeType        = 'DROP_SHADOW';
        mediaInfo.textTrackStyle.fontFamily      = 'CASUAL';
        mediaInfo.textTrackStyle.fontScale       = 1.0;
        mediaInfo.textTrackStyle.foregroundColor = '#FFFFFF';
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
        let e = Chromecast.eventListener[event] || []
        let i = e.indexOf(func)
        if (i > 0)
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