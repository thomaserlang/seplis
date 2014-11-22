(function($) {
    var SeplisPlay = function(video, play_servers, show_id, episode_number, start_pos, options) {
        var _this = this;

        var settings = $.extend({
        }, options);

        this.currentPlayServer = null;

        this.getDevice = (function() {
            if (navigator.userAgent.match(/(iPad|iPhone|iPod)/g)) {
                return 'apple';
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
        var device = this.getDevice();
        var offset_duration = 0;
        var stop_duration_update = false;
        var latest_position_stored = -1;
        var store_position_every = 10;

        var method = '/transcode';
        var startTime = 0;
        var watchedIncremented = false;
        var duration = 0;
      
        this.setStart = (function(startime) {
            startTime = startime;
            var url = _this.currentPlayServer.url+method+'?play_id='+_this.currentPlayServer.play_id+
                '&device='+device+'&session='+session+'&start='+startime.toString();
            video.attr(
                'src',                 
                url
            );
            if (method == '/transcode') offset_duration = startime;
            if ((device == 'apple') && (method == '/transcode')) {
                $.get(url);
            }
        });

        this.play = (function() {
            if ((device == 'apple') && (method == '/transcode')) {
                setTimeout(function(){
                    video.get(0).play();
                }, 1000);
            } else {
                video.get(0).play();
            }
        });

        this.setUp = (function(metadata) {
            duration = parseInt(metadata['format']['duration']).toString();
            $('.slider').attr(
                'max', 
                duration
            );
            $('.slider').show();
            if (metadata['format']['format_name'].indexOf('mp4') > -1) {
                method = '/play';
                $('.slider').hide();
            }

            video.on('timeupdate', function(event){
                if (stop_duration_update) {
                    return;
                }
                var time = offset_duration + parseInt(this.currentTime);
                if (((time % 10) == 0) && (latest_position_stored != time) && (time > 0) && !watchedIncremented) {
                    latest_position_stored = time;
                    var times = 0;
                    if (((time / 100) * 5) > (duration-time)) {
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
                $('.slider').val((
                    time
                ).toString());
                var format = 'mm:ss';
                if (time >= 3600) {
                    format = 'hh:mm:ss';
                }
                $('time_position').html(
                    (new Date)
                        .setSeconds(time)
                        .toString()
                );
            });
            video.on('canplay', function() { 
                video.currentTime = startTime;
            });
            $('.slider').on('touchstart', function(){
                stop_duration_update = true;
            });
            $('.slider').on('touchend', function(){
                stop_duration_update = false;            
            });
            $('.slider').on('mousedown', function(){
                stop_duration_update = true;
            });
            $('.slider').on('mouseup', function(){
                stop_duration_update = false;            
            });
            $('.slider').change(function(event){ 
                video.get(0).pause();
                $.get(_this.currentPlayServer.url+'/'+session+'/cancel');
                session = guid();
                var start = parseInt($(this).val());
                _this.setStart(start);
                watchedIncremented = false;
                _this.play();
            });
        });
        var checkServer = (function(play_server) {
            $.getJSON(play_server.url+'/metadata', {'play_id': play_server.play_id}, 
                function(data) {
                    if (_this.currentPlayServer) return;
                    $('.video').removeClass('hide');
                    $('.loading-video').hide();
                    _this.currentPlayServer = play_server;
                    _this.setUp(data);
                    _this.setStart(start_pos);
                    _this.play();
                }
            ).error(function(jqxhr, textStatus, error){
                if (_this.currentPlayServer) return;
                if (jqxhr.status == 404) {
                    $('.episode-404').removeClass('hide');
                } else {
                    $('.episode-no-connection').removeClass('hide');             
                }
                $('.loading-video').hide();
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