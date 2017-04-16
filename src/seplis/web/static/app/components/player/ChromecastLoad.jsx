import {getPlayServer} from './Player';
import {request} from 'api';
import {getUserId, guid} from 'utils';

var events = {
    ANY_CHANGED: 'anyChanged',
    AVAILABLE: 'isAvailable',
    IS_CONNECTED: 'isConnected',
    PLAYER_STATE: 'playerState',
    CURRENT_TIME: 'currentTime',
};

class ChromecastLoad {
 
    constructor(onInit) {
        this.onInit = onInit;
        this.loaded = false;
        if (!ChromecastLoad.initialized) {
            this.loadCastScript();
        } else {
            this.initCast(true);
        }
    }
 
    loadCastScript() {
        ChromecastLoad.initList.push(this);
        if (ChromecastLoad.loaded)
            return;
        ChromecastLoad.loaded = true;
        window['__onGCastApiAvailable'] = (isAvailable) => {
            // Temp fix for cast not reconnecting randomly
            setTimeout(() => {
                let sessionRequest = new chrome.cast.SessionRequest('45718FC5');
                let apiConfig = new chrome.cast.ApiConfig(
                    sessionRequest,
                    sessionListener,
                    receiverListener,
                    chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
                );
                chrome.cast.initialize(apiConfig, () => {
                    console.log('initialized');
                    ChromecastLoad.initialized = true;
                    for (let obj of ChromecastLoad.initList) {
                        obj.initCast(isAvailable);
                    }
                });
            }, 500);
        };
        let script = document.createElement('script');
        script.src = 'https://www.gstatic.com/cv/js/sender/v1/cast_sender.js';
        document.head.appendChild(script);
    }
 
    initCast(isAvailable) {
        this.loaded = isAvailable;
        if (!isAvailable) 
            return;
        if (this.onInit)
            this.onInit(this);
    }

    requestSession() {
        chrome.cast.requestSession(sessionListener);
    }

    isConnected() {
        if (!ChromecastLoad.session)
            return false;
        return ChromecastLoad.session.status == 'connected';
    }

    getSession() {
        return ChromecastLoad.session;
    }

    getMediaSession() {
        return ChromecastLoad.mediaSession;
    }

    getFriendlyName() {
        return ChromecastLoad.session.receiver.friendlyName;
    }

    getCurrentTime() {
        return ChromecastLoad.mediaSession.getEstimatedTime();
    }

    playOrPause(success, error) {
        if (ChromecastLoad.mediaSession.playerState == 'PLAYING')
            this.pause(success, error)
        else
            this.play(success, error);
    }    

    play(success, error) {
        ChromecastLoad.mediaSession.play(null, success, error);
    }

    pause(success, error) {
        ChromecastLoad.mediaSession.pause(null, success, error);
    }

    playEpisode(showId, episodeNumber, startTime) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected()) {
                console.log('Not connected to a cast device.');
                reject();
                return;
            }
            let url =`/1/shows/${showId}/episodes/${episodeNumber}/play-servers`;
            Promise.all([
                getPlayServer(url),
                request('/1/progress-token'),
                request(`/1/shows/${showId}`),
                request(`/1/shows/${showId}/episodes/${episodeNumber}`),
                request(`/1/shows/${showId}/episodes/${episodeNumber}/watched`),
                request(`/1/users/${getUserId()}/subtitle-lang/shows/${showId}`),
            ]).then((result) => {
                if (!startTime) {
                    if (result[4])
                        startTime = result[4].position
                    else
                        startTime = 0;
                }
                this.getSession().sendMessage(
                    'urn:x-cast:net.seplis.cast.info',
                    {
                        play: result[0]['playServer'],
                        metadata: result[0]['metadata'],
                        token: result[1]['token'],
                        type: 'episode',
                        show: result[2],
                        episode: result[3],
                        startTime: startTime,
                    },
                    () => {},
                    (error) => {console.log(error);},
                );
                let playUrl = result[0].playServer.play_server.url+'/play2'+
                    '?play_id='+result[0].playServer.play_id;
                playUrl += `&session=${guid()}`;
                if (startTime)
                    playUrl += `&start_time=${startTime}`;
                if (result[5]) {
                    playUrl += `&subtitle_lang=${result[5].subtitle_lang || ''}`;
                    playUrl += `&audio_lang=${result[5].audio_lang || ''}`;
                }
                console.log(playUrl);
                let request = new chrome.cast.media.LoadRequest(
                    this._playEpisodeMediaInfo(playUrl, result[2], result[3])
                );
                this.getSession().loadMedia(
                    request,
                    (mediaSession) => { 
                        mediaListener(mediaSession);
                        resolve(mediaSession); 
                    },
                    (e) => { reject(e); },
                );
            });
        });
    }

    _playEpisodeMediaInfo(url, show, episode) {
        var mediaInfo = new chrome.cast.media.MediaInfo(url);
        mediaInfo.metadata = new chrome.cast.media.TvShowMediaMetadata();
        mediaInfo.metadata.seriesTitle = show.title;
        mediaInfo.metadata.title = episode.title;
        mediaInfo.metadata.episode = episode.episode || episode.number;
        mediaInfo.metadata.originalAirdate = episode.air_date;
        mediaInfo.metadata.metadataType = chrome.cast.media.MetadataType.TV_SHOW;
        return mediaInfo;
    }

    addEventListener(event, func) {
        if (!(event in ChromecastLoad.eventListener))
            ChromecastLoad.eventListener[event] = [];
        let e = ChromecastLoad.eventListener[event] ;
        if (!ChromecastLoad.eventListener[event].includes(func))
            ChromecastLoad.eventListener[event].push(func);
    }
 
    removeEventListener(event, func) {
        let e = ChromecastLoad.eventListener[event] || [];
        i = e.indexOf(func);
        if (i > 0)
            e.splice(i, 1);
    }
}
ChromecastLoad.initialized = false;
ChromecastLoad.loaded = false;
ChromecastLoad.initList = [];
ChromecastLoad.session = null;
ChromecastLoad.mediaSession = null;
ChromecastLoad.eventListener = {};
ChromecastLoad.events = events;
ChromecastLoad.timerGetCurrentTime = null;

function sessionListener(session) {
    console.log('sessionListener');
    ChromecastLoad.session = session;
    if (session.media.length != 0) {
        mediaListener(session.media[0]);
    }
    ChromecastLoad.timerGetCurrentTime = setInterval(() => {
        if (!ChromecastLoad.mediaSession)
            return;
        if (ChromecastLoad.mediaSession.playerState == 'PLAYING')
            dispatchEvent(events.CURRENT_TIME, ChromecastLoad.mediaSession.getEstimatedTime());            
    }, 1000);
    session.addMediaListener(mediaListener);
    session.addUpdateListener(sessionUpdateListener);
    dispatchEvent(events.IS_CONNECTED, true);
}

function sessionUpdateListener(event) {
    if (ChromecastLoad.session.status !== chrome.cast.SessionStatus.CONNECTED) {
        ChromecastLoad.session = null;
        ChromecastLoad.mediaSession = null;
        dispatchEvent(events.IS_CONNECTED, false);
    }
}

function mediaListener(mediaSession) {
    console.log('mediaListener');
    ChromecastLoad.mediaSession = mediaSession;
    mediaSession.addUpdateListener(mediaSessionUpdateListener);        
    dispatchEvent(events.CURRENT_TIME, ChromecastLoad.mediaSession.getEstimatedTime());            
    // Chrome iOS fix
    mediaSessionUpdateListener()
}

function mediaSessionUpdateListener() {
    console.log('mediaSessionUpdateListener');
    dispatchEvent(
        events.PLAYER_STATE, 
        ChromecastLoad.mediaSession.playerState
    );
}

function receiverListener(state) {
    console.log('receiverListener');
    if (state == 'available')
        dispatchEvent(events.AVAILABLE, true)
    else        
        dispatchEvent(events.AVAILABLE, false);
}

function mediaStatusUpdateListener(isAlive) {
    console.log(isAlive);
    console.log('mediaStatusUpdateListener');
}

function dispatchEvent(event, data) {    
    let e = {
        field: event,
        value: data,
    }    
    _dispatchEvent('anyChanged', e);
    _dispatchEvent(event, e);
}

function _dispatchEvent(event, data) {
    let e = ChromecastLoad.eventListener[event] || [];
    e.forEach(f => {
        try {
            f(data);
        } catch (e) {
            console.log(e);            
        }
    });
}
 
export default ChromecastLoad;