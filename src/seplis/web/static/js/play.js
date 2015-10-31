(function($) {
    var SeplisPlay = function(video, play_servers, show_id, episode_number, start_pos, chromecastAppId, options) {
        var _this = this;

        var settings = $.extend({
        }, options);

        var currentPlayServer;

        var getDevice = (function() {
            var ua = navigator.userAgent;
            if (ua.match(/(iPad|iPhone|iPod)/g)) {
                return 'hlsmp4';
            } 
            return 'default';
        });
        var guid = (function() {
            function s4() {
                return Math.floor((1 + Math.random()) * 0x10000)
                       .toString(16)
                       .substring(1);
            }
            return function() {
                return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
                    s4() + '-' + s4() + s4() + s4();
            };
        })();
        var getCookie = (function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        });

        var session = guid();
        var device = getDevice();
        var offsetDuration = 0;
        var lastPosStored = -1;
        var store_position_every = 10;

        var method = 'transcode';
        var startTime = 0;
        var watchedIncremented = false;
        var duration = 0;
        var metadata;
        var player;
        var controlsHideTimer;

        var enableMousemoveChangeSlider = false;
        var disableChangeSlider = false;
        var currentTime;
        
        var playUrl = function(){
            return _playUrl(method, device, startTime, session);
        };

        var _playUrl = function(method, device, starttime, session) {
            var url;
            startTime = starttime;
            if (method == 'transcode') {
                url = currentPlayServer.url+'/transcode?play_id='+
                    currentPlayServer.play_id+'&device='+device+'&session='+
                    session+'&start='+starttime.toString();
                offsetDuration = starttime;
            } else {
                url = currentPlayServer.url+'/play?play_id='+currentPlayServer.play_id;
                if (starttime>0) {
                    url = url +'#t='+starttime.toString();
                }
            }
            return url;
        }

        var changeSlider = (function(time) {
            if (disableChangeSlider)
                return;
            time = parseInt(time);
            var norm = $('.player-slider').width() / duration;
            var dotNorm = $('.player-slider-dot').width() / duration;
            var x = time*norm;
            if (x > $('.player-slider').width()) {
                x = $('.player-slider').width()
            }
            $('.player-slider-dot').css('left', x-(time*dotNorm));
            $('.player-progress').css('width', x);            
            
            var t = duration - time;             
            $('.player-timeleft').text(getTimeText(t));
            currentTime = time;
        });

        var getTimeText = (function(time) {
            var format = 'mm:ss';
            if (time >= 3600) format = 'HH:mm:ss';
            return moment(time*1000).utc().format(format);
        });

        var ChangeVolume = (function(volume) {
            var remClases = "glyphicon glyphicon-volume-up glyphicon-volume-down glyphicon-volume-off";
            var icon = $('.player-volume').find('i');
            icon.removeClass(remClases);
            if ((volume == 0) || (player.muted)) {
                icon.addClass("glyphicon glyphicon-volume-off");
                player.muted = true;
            } else if (volume <= 0.5) {
                icon.addClass("glyphicon glyphicon-volume-down");
            } else {
                icon.addClass("glyphicon glyphicon-volume-up");                    
            }
            $('.player-volume-slider').val(volume);
            localStorage.setItem('player_volume_default', volume);
            player.volume = volume;
        });

        this.setUp = (function(metadata_, starttime) {
            metadata = metadata_;
            startTime = parseInt(starttime);
            duration = parseInt(metadata['format']['duration']).toString();
            if (isMobile()) {
                $('.player-volume').hide();
            }
            if (metadata['format']['format_name'].indexOf('mp4') > -1) {
                method = 'play';
            }
            player = video.get(0);
            if (!isMobile())
                player.volume = localStorage.getItem('player_volume_default') || 1;
            ChangeVolume(player.volume);
            video.on('timeupdate', function(){
                if (video.attr('src') == undefined)
                    return;
                ShowPauseButton();
                $('.player-loading').hide();
                $('.player-casting-to').hide();
                var time = offsetDuration + parseInt(this.currentTime);
                if (((time % 10) == 0) && (lastPosStored != time) && 
                    (time > 0) && !watchedIncremented &&
                    (((startTime / 100) * 10) <= duration-startTime)) {
                    lastPosStored = time;
                    var times = 0;
                    if (((time / 100) * 10) > (duration-time)) {
                        watchedIncremented = true;
                        times = 1;
                        time = 0;
                    }
                    $.post('/api/user/watching', {
                        'show_id': show_id,
                        'episode_number': episode_number,
                        'position': time,
                        'times': times,
                        '_xsrf': getCookie('_xsrf'),
                    });
                }
                if (!enableMousemoveChangeSlider)
                    changeSlider(time);
            });
            video.on('error', function(event) {
                $('.player-play-server-error').show();
                $('.player-loading').hide();
            })
            video.on('pause', function(){                
                if (video.attr('src') == undefined)
                    return;
                ShowPlayButton();
                showControls();
            });
            video.on('play', function(){    
                if (video.attr('src') == undefined)
                    return;
                ShowPauseButton();
                hideErrors();                
                $('.player-loading').show();
                startHideControlsStartTimer();
            });
            video.on('volumechange', function(){
                ChangeVolume(player.volume);
            });
            video.on('webkitfullscreenchange mozfullscreenchange fullscreenchange', function(){
                var state = document.fullScreen || document.mozFullScreen || document.webkitIsFullScreen;
                if (state) {
                    $('.player-fullscreen-button').addClass('hidden');
                    $('.player-windowed-button').removeClass('hidden');  
                } else {
                    $('.player-windowed-button').addClass('hidden');
                    $('.player-fullscreen-button').removeClass('hidden');                  
                }
                startHideControlsStartTimer();
            });
            $(window).on('keypress', function(event){
                if (event.which == 32) togglePlay();
            });
            $('.player-volume-slider').on('change mousemove touchmove', function(event){
                ChangeVolume($(this).val());
                if (event.type == 'change') 
                    player.muted = false;                
            });
            $('.player-volume i').click(function(){
                player.muted = !player.muted;
                if ((!player.muted) && (player.volume === 0)) {
                    player.volume = 1;
                }
            });
            $('.player-play-pause-button').click(function(){
                togglePlay();
            });
            $('.player-fullscreen-button').click(function(){
                if (player.requestFullScreen) {
                    player.requestFullScreen();
                } else if (player.mozRequestFullScreen) {
                    player.mozRequestFullScreen();
                } else if (player.webkitRequestFullScreen) {
                    player.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
                } else if (player.webkitEnterFullscreen) {
                    player.webkitEnterFullscreen();
                }
            });
            $('.player-windowed-button').click(function(){
                if (document.cancelFullScreen) {
                    document.cancelFullScreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.webkitCancelFullScreen) {
                    document.webkitCancelFullScreen();
                }
            });
            $(video).on('mousemove', function(event){
                showControls();
                event.stopImmediatePropagation();
            });
            $(video).on('click touchstart', function(event){
                event.stopPropagation();
                event.preventDefault();
                if ($('.player-back').is(':visible')) {
                    if ((player.paused) || (seplisCast.isCasting()))
                        return;
                    hideControls();
                } else {
                    showControls();
                }               
            });

            seplisCast.onCast = function(callback){
                var st = parseInt(currentTime);
                playerPause();
                setTimeout(showCastingScreen, 500);
                if (method == 'transcode') {  
                    if (device == 'hlsmp4')    
                        $.get(currentPlayServer.url+'/'+session+'/cancel');
                }
                api.get('/api/progress-token', null, {
                    done: (function(data) {
                        callback({
                            'show_id': show_id,
                            'episode_number': episode_number,
                            'start_time': st,
                            'token': data.token,
                            'play_url': _playUrl(
                                method, 
                                'default',
                                st,
                                guid()
                            ),
                            'method': method,
                            'duration': parseInt(duration),
                            'api_url': data['api_url'],
                            'user_id': data['user_id'],
                        });
                    })
                });
            }
            seplisCast.onProgress = function(currenttime){  
                if (enableMousemoveChangeSlider)
                    return;
                if (currenttime == 0)
                    return;
                disableChangeSlider = false;
                startTime = currenttime|0;
                offsetDuration = 0;
                changeSlider(currenttime);
                $('.player-casting-to').show();
                hideErrors();
            }
            seplisCast.onPlay = function() {
                ShowPauseButton();
                enableMousemoveChangeSlider = false;
                disableChangeSlider = false;
            }            
            seplisCast.onPause = function() {
                ShowPlayButton();
            }
            seplisCast.onReconnected = function() {                
                player.pause();
                setTimeout(showCastingScreen, 100);
            }
            seplisCast.onStopped = function() {
                $('.player-casting-to').hide();
            }
            seplisCast.onLoading = function(){
                ShowPauseButton();
                $('.player-loading').show();
            }
            seplisCast.init($('.player-cast'), chromecastAppId);
            changeSlider(startTime);
            if (!seplisCast.alreadyCasting()) {
                video.attr('src', playUrl());
            } else {
                showCastingScreen();
                hideControls();
                $('.player-back').show();
                setTimeout(function(){
                    if (!seplisCast.isCasting()) {
                        playerStart();
                        showControls();
                        $('.player-loading').hide();
                        $('.player-casting-to').hide();
                    }
                }, 2000);
            }
            HlsPing();
        });

        var showCastingScreen = function() {
            showControls();
            if (video.attr('src') != undefined)
                video.attr('src', undefined);
            $('.player-casting-to').show();
            $('.casting-to-name').text(seplisCast.deviceName());
            clearTimeout(controlsHideTimer);        
        }

        var ShowPauseButton = function() {
            $('.player-pause-button').removeClass('hidden');
            $('.player-play-button').addClass('hidden');
        }

        var ShowPlayButton = function() {
            $('.player-play-button').removeClass('hidden');
            $('.player-pause-button').addClass('hidden');
        }

        var startHideControlsStartTimer = (function(){
            clearTimeout(controlsHideTimer);
            controlsHideTimer = setTimeout(function(){
                if (player.paused || seplisCast.isCasting())
                    return;               
                hideControls();
            }, 3000);
        });
        var hideControls = (function(){
            clearTimeout(controlsHideTimer);
            $('.player-controls-wrapper').css('visibility', 'hidden');
            $('.player-slider-time').css('visibility', 'hidden');
            $('.player-back').hide();
        });

        var showControls = (function(){
            startHideControlsStartTimer();
            $('.player-controls-wrapper').css('visibility', 'visible');
            $('.player-back').show();
        });

        $('.player-controls-wrapper').on('mouseenter', function(){
            clearTimeout(controlsHideTimer);
        });

        $('.player-controls-wrapper').on('mouseleave', function(event){
            startHideControlsStartTimer();
        });

        $('.player-back').on('click', function(){
            location.href = '/show/'+show_id;
        });
        
        var playerPause = function(){
            if (player.paused === true)
                return;
            player.pause();
            if (method == 'transcode') {  
                if (device == 'hlsmp4')    
                    $.get(currentPlayServer.url+'/'+session+'/cancel');
                startTime = parseInt(player.currentTime+offsetDuration);  
            }
        }

        var playerStart = function(){
            $('.player-loading').show();
            if ((method == 'transcode') || (video.attr('src') == undefined))
                video.attr('src', playUrl());
            if ((device == 'hlsmp4') && (method == 'transcode')) {
                setTimeout(function(){
                    player.play();
                }, 1000);
            } else {
                player.play();
            }
        }

        var togglePlay = (function(){
            if (!seplisCast.isCasting()) {
                if (!player.paused && (player.readyState != 0)) {
                    playerPause();
                } else {
                    playerStart();
                }
            } else {
                seplisCast.togglePlay();
            }
        });

        var startAtSliderPos = (function(event){
            var x = getEventXOffset(event);
            if (x < 0) return;
            var norm = duration / $('.player-slider').width();
            var time = x * norm;
            time = parseInt(time);
            changeSlider(time);
            if (seplisCast.isCasting()) {
                disableChangeSlider = true;
                startTime = time;
                session = guid();
                seplisCast.play();
            } else {
                if (method == 'play') {
                    player.currentTime = time;
                } else {
                    if (player.paused === false)
                        togglePlay();
                    startTime = time;
                    session = guid();
                    togglePlay();
                }
            }
        });

        var getEventXOffset = (function(event) {
            if (event.type.match('^touch')) {
                event = event.originalEvent.touches[0] || 
                    event.originalEvent.changedTouches[0];
            }
            var x = event.clientX - $('.player-slider').offset().left;
            if (x > $('.player-slider').width())
                x = $('.player-slider').width();
            return x;
        });

        $('.player-slider').click(function(event){
            startAtSliderPos(event);
        });

        $(window).resize(function() {
            changeSlider(currentTime);
        });

        $('.player-slider').on('mousedown touchstart', function(event){
            enableMousemoveChangeSlider = true;
            disableChangeSlider = false;
            if (event.type == 'touchstart')
                clearTimeout(controlsHideTimer);
        });
        $('.player-slider').on('mousemove touchmove', function(event){
            event.stopPropagation();
            event.preventDefault();       
            $('.player-slider-time').css('visibility', 'visible');

            var x = getEventXOffset(event);
            if (x < 0) return;
            var norm = duration / $('.player-slider').width();
            $('.player-slider-time').css(
                'left', 
                x - ($('.player-slider-time').outerWidth() / 2)
            );
            $('.player-slider-time').text(
                getTimeText(norm*x)
            );
            if (enableMousemoveChangeSlider)
                changeSlider(norm*x);
        });
        $(document).on('mouseup', function(){
            enableMousemoveChangeSlider = false;
        });
        $('.player-slider').on('touchend', function(event){
            startHideControlsStartTimer();
            enableMousemoveChangeSlider = false;
            startAtSliderPos(event);            
            $('.player-slider-time').css('visibility', 'hidden');
        });
        $('.player-slider').on('mouseleave', function(){            
            $('.player-slider-time').css('visibility', 'hidden');
        });

        var HlsPing = (function(){
            if (device != 'hlsmp4') return;
            if (player.paused === false) {
                $.get(currentPlayServer.url+'/'+session+'/ping');
            }
            setTimeout(function(){
                HlsPing();
            }, 5000);
        });

        var hideErrors = (function(){
            $('.player-episode-404').hide();
            $('.player-play-server-error').hide();  
            $('.player-loading').hide();
        });

        var checkServer = (function(play_server) {
            hideErrors(); 
            $('.player-loading').show();
            $.getJSON(play_server.url+'/metadata', {'play_id': play_server.play_id}, 
                function(data) {
                    if (currentPlayServer) return; 
                    hideErrors();
                    currentPlayServer = play_server;
                    _this.setUp(data, start_pos);
                    player.play();
                }
            ).error(function(jqxhr, textStatus, error){
                if (currentPlayServer) return;
                if (jqxhr.status == 404) {
                    $('.player-episode-404').show();
                } else {
                    $('.player-play-server-error').show();             
                }
                $('.player-loading').hide();
            });
        });

        for (i in play_servers) {
            var ps = play_servers[i];
            if (ps.url.substr(ps.url.length - 1) == '/') {
                ps.url = ps.url.substr(0, ps.url.length - 1);
            }
            checkServer(ps);
        }
    }

    $.fn.seplis_play = function(play_servers, show_id, episode_number, start_pos, chromecastAppId, options) {
        return this.each(function(){
            var video = $(this);
            if (video.data('seplis_play')) return;
            var seplis_play = new SeplisPlay(
                video, 
                play_servers,
                show_id,
                episode_number,
                start_pos,
                chromecastAppId,
                options
            );
            video.data('seplis_play', seplis_play);
        }); 
    };
 
}(jQuery));