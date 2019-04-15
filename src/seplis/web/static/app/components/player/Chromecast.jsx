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
            ]).then((result) => {
                if (!startTime) {
                    if (result[4])
                        startTime = result[4].position
                    else
                        startTime = 0
                }
                this.getSession().sendMessage(
                    'urn:x-cast:net.seplis.cast.info',
                    {
                        play: result[0]['playServer'],
                        metadata: {
                            format: {
                                duration: result[0]['metadata']['format']['duration'],
                            },
                            streams: result[0]['metadata']['streams'],
                        },
                        token: result[1]['token'],
                        type: 'episode',
                        show: {
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
                    },
                    () => {},
                    (e) => {reject(e)},
                )
                let playUrl = result[0].playServer.play_url+'/play'+
                    '?play_id='+result[0].playServer.play_id
                playUrl += `&session=${guid()}`
                if (startTime)
                    playUrl += `&start_time=${startTime}`
                if (result[5]) {
                    playUrl += `&subtitle_lang=${result[5].subtitle_lang || ''}`
                    playUrl += `&audio_lang=${result[5].audio_lang || ''}`
                }
                let request = new chrome.cast.media.LoadRequest(
                    this._playEpisodeMediaInfo(playUrl, result[2], result[3])
                )
                this.getSession().loadMedia(
                    request,
                    (mediaSession) => { 
                        mediaListener(mediaSession)
                        resolve(mediaSession) 
                    },
                    (e) => { reject(e) },Chromecast
                )
            }).catch((e) => {
                reject(e)
            })
        })
    }

    _playEpisodeMediaInfo(url, show, episode) {
        var mediaInfo = new chrome.cast.media.MediaInfo(url)
        mediaInfo.metadata = new chrome.cast.media.TvShowMediaMetadata()
        mediaInfo.metadata.seriesTitle = show.title
        mediaInfo.metadata.title = episode.title
        mediaInfo.metadata.episode = episode.episode || episode.number
        mediaInfo.metadata.originalAirdate = episode.air_date
        mediaInfo.metadata.metadataType = chrome.cast.media.MetadataType.TV_SHOW
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
    // Chrome iOS fix
    mediaSessionUpdateListener()
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