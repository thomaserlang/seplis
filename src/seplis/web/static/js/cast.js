(function(seplisCast, $, undefined) {

    var updateCurrentTimeTimer = null;
    var updateStoredSessionTimer = null;
    var currentMediaSession = null;
    var namespace = 'urn:x-cast:net.seplis.cast.data';
    var session = null;
    var data = null;
    var castButton = null;

    onCast = null;
    onProgress = null;
    onPlay = null;
    onPause = null;
    onReconnected = null;
    onStopped = null;
    onLoading = null;

    seplisCast.init = function(_castButton, appId) {
        castButton = _castButton;
        startUpdateStoredSessionTimer();
        setTimeout(function(){
            if (!chrome.cast || !chrome.cast.isAvailable) {
                console.log('Chrome cast not loaded...');
            }
            console.log('init started');

            var sessionRequest = new chrome.cast.SessionRequest(
                appId
            );
            var apiConfig = new chrome.cast.ApiConfig(
                sessionRequest,
                sessionListener,
                receiverListener,
                chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED
            );
            chrome.cast.initialize(
                apiConfig, 
                onInitSuccess, 
                onError
            );
        }, 1000);
    };

    seplisCast.isCasting = function() {
        if (!session)
            return false;
        return true;
    }

    seplisCast.togglePlay = function() {
        if (!currentMediaSession) {
            play();
            return;
        }
        var ps = currentMediaSession.playerState;
        if (ps == 'PLAYING') {
            if (data.method == 'transcode') {
                stop();
            } else {
                currentMediaSession.pause(
                    null,
                    null,
                    onError
                );
            }
        } else if (['PAUSED', 'IDLE'].indexOf(ps) >= 0) {
            if (data.method == 'transcode') {
                play();
            } else {
                currentMediaSession.play(
                    null,
                    null,
                    onError
                ); 
            }
        }
    }

    seplisCast.alreadyCasting = function() {
        if (typeof(Storage) == 'undefined')
            return false;
        var storedSession = JSON.parse(
            localStorage.getItem('storedSession')
        );
        if (storedSession) {
            var dateString = storedSession.timestamp;
            var now = new Date().getTime();
            if (now - dateString < 3600000)
                return true;
        }
        return false;
    }

    seplisCast.play = function(){
        play();
    }

    seplisCast.deviceName = function(){
        if (!session)
            return;
        return session.receiver.friendlyName;
    }

    function updateCurrentTime() {
        if (!session || !currentMediaSession || !data || !currentMediaSession.media) {
            return;
        }
        currenttime = currentMediaSession.getEstimatedTime();
        if (data.method == 'transcode')
            currenttime += data.start_time;
        if (seplisCast.onProgress)
            seplisCast.onProgress(
                currenttime
            );
    }

    function stopApp() {
        session.stop(onStopAppSuccess, onError);
        if (updateCurrentTimeTimer) {
            clearInterval(updateCurrentTimeTimer);
            updateCurrentTimeTimer = null;
        }
    }

    function play() {
        if (seplisCast.onCast == null) {
            console.log('onCast event not set.');
            return;
        }        
        if (seplisCast.onLoading)
            seplisCast.onLoading();
        seplisCast.onCast((function(d){
            data = d;
            localStorage.setItem('last_cast_url', window.location.pathname);
            updateCurrentTime();
            session.sendMessage(
                namespace, 
                {
                    'method': 'setdata',
                    'data': data
                }
            );
            var mediaInfo = new chrome.cast.media.MediaInfo(
                data.play_url   
            );
            mediaInfo.metadata = new chrome.cast.media.GenericMediaMetadata();
            mediaInfo.metadata.metadataType = chrome.cast.media.MetadataType.GENERIC;
            mediaInfo.contentType = '';
            var request = new chrome.cast.media.LoadRequest(mediaInfo);
            session.loadMedia(
                request,
                onMediaDiscovered.bind(this, 'loadMedia'),
                onMediaError
            );
        }));        
    }

    function receiverMessage(namespace, message) {
        var msg = JSON.parse(message);
        switch (msg.method) {
            case 'setdata':
                data = msg.data; 
                break;
        }
    };

    function onMediaDiscovered(how, mediaSession) {
        mediaSession.addUpdateListener(onMediaStatusUpdate);
        currentMediaSession = mediaSession;
    }

    function onMediaError(e) {
        console.log('media error');
    }

    function onMediaStatusUpdate(isAlive) {
        if (isAlive) {
            if (currentMediaSession.playerState == 'PLAYING') {
                if (!updateCurrentTimeTimer) {
                    updateCurrentTime();
                    updateCurrentTimeTimer = setInterval(
                        updateCurrentTime, 
                        1000
                    );
                    saveSession(session);
                }
                if (seplisCast.onPlay)
                    seplisCast.onPlay();
            } else if (currentMediaSession.playerState == 'PAUSED') {
                if (seplisCast.onPause)
                    seplisCast.onPause();
            }
        } else {
            if (seplisCast.onPause)
                seplisCast.onPause();
        }
    }

    function onInitSuccess() {
        console.log('init success');
    }

    function onError(e) {
        console.log('Error' + e);
    }

    function onSuccess(message) {
        console.log(message);
    }

    function onStopAppSuccess() {
        removeSavedSession();
    }

    function sessionListener(e) {
        console.log('New session ID: ' + e.sessionId);
        session = e;
        saveSession(session);
        session.addMessageListener(namespace, receiverMessage);
        if (session.media.length != 0) {
            console.log('joining session');
            onMediaDiscovered('sessionListener', session.media[0]);
            if (!updateCurrentTimeTimer) {
                updateCurrentTime();
                updateCurrentTimeTimer = setInterval(
                    updateCurrentTime, 
                    1000
                );
                if (seplisCast.onPlay) {
                    seplisCast.onPlay();
                }
            }
        } else {
            if (window.location.pathname != localStorage.getItem('last_cast_url')) {
                play();
            }
        }
        session.addMediaListener(
            onMediaDiscovered.bind(this, 'addMediaListener')
        );
        session.addUpdateListener(
            sessionUpdateListener.bind(this)
        );
        session.sendMessage(namespace, {
            'method': 'getdata',
        });
        if (seplisCast.onReconnected)
            seplisCast.onReconnected();

    }

    function sessionUpdateListener() {
        if (session.status == chrome.cast.SessionStatus.STOPPED) {
            sessionStopped();
        } else {
            if (!updateCurrentTimeTimer) {
                updateCurrentTime();
                updateCurrentTimeTimer = setInterval(
                    updateCurrentTime.bind(this),
                    1000
                );
            }
            if (seplisCast.onPlay)
                seplisCast.onPlay();
        }        
    }

    function receiverListener(e) {
        if (e === 'available') {
            console.log('receiver found');
            castButton.css('display', 'block');        
            castButton.on('click', launchApp);
        }
        else {
            console.log('receiver list empty');
        }
    }

    function launchApp() {
        console.log('launching app...');
        chrome.cast.requestSession(
            onRequestSessionSuccess, 
            onLaunchError
        );
    }

    function onRequestSessionSuccess(e) {
        console.log('session success: ' + e.sessionId);
        session = e;
        saveSession(session);
        session.addUpdateListener(
            sessionUpdateListener.bind(this)
        );
        if (session.media.length != 0) {
            onMediaDiscovered('onRequestSession', session.media[0]);
        }
        session.addMediaListener(
            onMediaDiscovered.bind(this, 'addMediaListener')
        );
        play();
    }

    function onLaunchError() {
        console.log('Launch error.');
        removeSavedSession();
    } 

    function stop() {
        if (!currentMediaSession)
            return;
        currentMediaSession.stop(
            null,
            null,
            onError
        );
        if (seplisCast.onPause)
            seplisCast.onPause();
        console.log('media stopped');
        if (updateCurrentTimeTimer) {
            clearInterval(updateCurrentTimeTimer);
            updateCurrentTimeTimer = null;
        }
    }

    function mediaCommandSuccessCallback(info) {
        console.log(info);
    }

    function saveSession(session) {
        if (typeof(Storage) == 'undefined')
            return;
        var obj = {
            'id': session.sessionId, 
            'timestamp': new Date().getTime()
        };
        localStorage.setItem('storedSession', JSON.stringify(obj));
        startUpdateStoredSessionTimer();
    }

    function startUpdateStoredSessionTimer() {
        if (updateStoredSessionTimer)
            return;
        updateStoredSessionTimer = setInterval((function() {
            if (!session) {
                removeSavedSession();
                clearInterval(updateStoredSessionTimer);
                updateStoredSessionTimer = null;
            } else {
                saveSession(session);
            }
        }), 2000);
    }

    function removeSavedSession() {
        if (typeof(Storage) == 'undefined')
            return;
        localStorage.removeItem('storedSession');
    }

    function sessionStopped() {
        session = null;
        currentMediaSession = null;
        if (updateCurrentTimeTimer) {
            clearInterval(updateCurrentTimeTimer);
            updateCurrentTimeTimer = null;
        }
        removeSavedSession();
        if (updateStoredSessionTimer) {
            clearInterval(updateStoredSessionTimer);
            updateStoredSessionTimer = null;
        }
        if (seplisCast.onPause) 
            seplisCast.onPause();
        if (seplisCast.onStopped)
            seplisCast.onStopped();
        localStorage.removeItem('last_cast_url');
    }

}(window.seplisCast = window.seplisCast || {}, jQuery));