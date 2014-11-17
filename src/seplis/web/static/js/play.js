(function($) {
    var SeplisPlay = function(video, url, play_id, options) {
        var _this = this;

        var settings = $.extend({
        }, options);

        if (url.substr(url.length - 1) == '/') {
            url = url.substr(0, url.length - 1);
        }

        this.get_device = (function() {
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

        var session = guid();
        var device = this.get_device();
        var offset_duration = 0;
        var stop_duration_update = false;

        this.setUp = (function(metadata) {
            $('.slider').attr(
                'max', 
                parseInt(metadata['format']['duration']).toString()
            );
            var method = '/transcode';
            $('.slider').show();
            if (metadata['format']['format_name'].indexOf('mp4') > -1) {
                method = '/play';
                $('.slider').hide();
            }
            
            var src = url+method+'?play_id='+
                play_id+'&device='+device+'&session='+session;
            $('video').attr('src', src);

            video.on('timeupdate', function(event){
                if (stop_duration_update) {
                    return;
                }
                var time = offset_duration + parseInt(this.currentTime);
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
                $.get(url+'/'+session+'/cancel');
                session = guid();
                var start = parseInt($(this).val());
                video.attr(
                    'src', 
                    url+method+'?play_id='+play_id+
                    '&device='+device+'&session='+session+'&start='+start.toString()
                );
                offset_duration = start;            
                video.get(0).play();
            });
        });

        $.getJSON(url+'/metadata', {'play_id': play_id}, 
            function(data) {
                _this.setUp(data);
            }
        );

    }

    $.fn.seplis_play = function(url, play_id, options) {
        return this.each(function(){
            var video = $(this);
            if (video.data('seplis_play')) return;
            var seplis_play = new SeplisPlay(
                video, 
                url, 
                play_id, 
                options
            );
            video.data('seplis_play', seplis_play);
        }); 
    };
 
}(jQuery));