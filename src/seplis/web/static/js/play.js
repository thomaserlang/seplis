(function($) {
    var SeplisPlay = function(video, play_servers, show_id, episode_number, start_pos, options) {
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
        
        var playUrl = (function(){
            var url;
            if (method == 'transcode') {
                url = currentPlayServer.url+'/transcode?play_id='+
                    currentPlayServer.play_id+'&device='+device+'&session='+
                    session+'&start='+startTime.toString();
                offsetDuration = startTime;
            } else {
                url = currentPlayServer.url+'/play?play_id='+currentPlayServer.play_id;
                if (startTime>0) {
                    url = url +'#t='+startTime.toString();
                }
            }
            return url;
        });

        var changeSlider = (function(time) {
            time = parseInt(time);
            var norm = $('.player-slider').width() / duration;
            var dotNorm = $('.player-slider-dot').width() / duration;
            $('.player-slider-dot').css('left', (time*norm)-(time*dotNorm));
            $('.player-progress').css('width', (time*norm));
            var format = 'mm:ss';
            var t = duration - time;
            if (t >= 3600) format = 'hh:mm:ss';                
            $('.player-timeleft').html(moment(t*1000).format(format));
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
            $('.player-volume-slider').val(player.volume);
            video.trigger('volumechange');
            video.on('timeupdate', function(){
                console.log('timeupdate...');
                $('.player-loading').hide();
                var time = offsetDuration + parseInt(this.currentTime);
                if (((time % 10) == 0) && (lastPosStored != time) && 
                    (time > 0) && !watchedIncremented) {
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
                changeSlider(time);
            });
            video.on('ended', function() {
                
            });
            video.on('error', function(event) {
                $('.player-play-server-error').show();
                $('.player-loading').hide();
            })
            video.on('pause', function(){
                $('.player-play-button').removeClass('hidden');
                $('.player-pause-button').addClass('hidden');
                showControls();
            });
            video.on('play', function(){
                $('.player-pause-button').removeClass('hidden');
                $('.player-play-button').addClass('hidden');
                hideErrors();
            });
            video.on('volumechange', function(){
                var remClases = "glyphicon glyphicon-volume-up glyphicon-volume-down glyphicon-volume-off";
                var icon = $('.player-volume').find('i');
                icon.removeClass(remClases);
                if ((player.volume == 0) || (player.muted)) {
                    icon.addClass("glyphicon glyphicon-volume-off");
                    player.muted = true;
                } else if (player.volume <= 0.5) {                    
                    icon.addClass("glyphicon glyphicon-volume-down");
                } else {
                    icon.addClass("glyphicon glyphicon-volume-up");                    
                }
                $('.player-volume-slider').val(player.volume);
                localStorage.setItem('player_volume_default', player.volume);
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
                console.log(event.which);
                if (event.which == 32) togglePlay();
            });
            $('.player-volume-slider').on('change mousemove touchmove', function(event){
                player.volume = $(this).val();
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
            $('.player-slider').click(function(event){
                console.log($('.player-controls-wrapper').css('visibility'));
                var norm = duration / $('.player-slider').width();
                var time = (event.pageX - $(this).offset().left) * norm;
                time = parseInt(time);
                changeSlider(time);
                if (method == 'play') {
                    player.currentTime = time;
                } else {
                    if (player.paused === false)
                        togglePlay();
                    startTime = time;
                    session = guid();
                    watchedIncremented = false;
                    togglePlay();
                }
            });
            $(video).on('mousemove', function(event){
                showControls();
                event.stopImmediatePropagation();
            });
            $(video).on('click', function(event){
                if ($('.player-back').is(':visible')) {
                    if (player.paused === true) return;
                    hideControls();
                } else {
                    showControls();
                }               
            });
            $(video).on('webkitExitFullScreen', function(){
                console.log('exit fullscreen');
                alert('exit');
            });
            $('.player-back').on('click', function(){
                alert('Go back to something...');
            });
            startHideControlsStartTimer();
            changeSlider(startTime);
            var url = playUrl();
            video.attr('src', url);
            video.load();
        });

        var startHideControlsStartTimer = (function(){
            clearTimeout(controlsHideTimer);
            controlsHideTimer = setTimeout(function(){
                if (player.paused) return;               
                hideControls();
            }, 3000);
        });
        var hideControls = (function(){
            clearTimeout(controlsHideTimer);
            $('.player-controls-wrapper').css('visibility', 'hidden');
            $('.player-back').hide();
        });

        var showControls = (function(){
            startHideControlsStartTimer();
            $('.player-controls-wrapper').css('visibility', 'visible');
            $('.player-back').show();
        });

        var togglePlay = (function(){
            if (player.paused === false) {
                player.pause();
                if (method == 'transcode') {      
                    $.get(currentPlayServer.url+'/'+session+'/cancel');
                    startTime = parseInt(player.currentTime+offsetDuration);  
                }
            } else {
                $('.player-loading').show();
                if ((method == 'transcode'))
                    video.attr('src', playUrl());
                if ((device == 'hlsmp4') && (method == 'transcode')) {
                    setTimeout(function(){
                        player.play();
                    }, 1000);
                } else {
                    player.play();
                }
            }
        });

        var hideErrors = (function(){
            $('.player-episode-404').hide();
            $('.player-play-server-error').hide();  
            $('.player-loading').hide();
        });

        var checkServer = (function(play_server) {
            $('.player-episode-404').hide();
            $('.player-play-server-error').hide();  
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

    $.fn.seplis_play = function(play_servers, show_id, episode_number, start_pos, options) {
        return this.each(function(){
            var video = $(this);
            if (video.data('seplis_play')) return;
            var seplis_play = new SeplisPlay(
                video, 
                play_servers,
                show_id,
                episode_number,
                start_pos,
                options
            );
            video.data('seplis_play', seplis_play);
        }); 
    };
 
}(jQuery));