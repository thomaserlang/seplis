$('.fan-button').on('click', '.btn-fan', function(event){
    $(this).blur();
    var _this = this;
    api.post(
        '/api/fan',
        $.param({
            show_id: $(_this).attr('show-id'),
            do: 'fan'
        }),
        {
            done: function(){
                var fan_count = $(_this).parent().find('.btn-fan-count');
                fan_count.html(parseInt(fan_count.html())+1);
                $(_this).toggleClass('btn-fan btn-unfan');
            }
        }
    );
});

$('.fan-button').on('click', '.btn-unfan', function(event){
    $(this).blur();
    var _this = this;
    api.post(
        '/api/fan',
        $.param({
            show_id: $(_this).attr('show-id'),
            do: 'unfan'
        }),
        {
            done: function(){
                var fan_count = $(_this).parent().find('.btn-fan-count');
                fan_count.html(parseInt(fan_count.html())-1);                
                $(_this).toggleClass('btn-unfan btn-fan');
            }
        }
    );
});

$('.season-episodes').on('click', '.btn-not-watched', function(event){
    $(this).blur();
    var btn = $(this)
    btn.button('loading');
    api.post(
        '/api/watched',
        $.param({
            show_id: btn.attr('show-id'),
            number: btn.attr('episode-number'),
            do: 'incr'
        }),
        {
            done: function(){
                var watched_count = btn.parent().find('.btn-watched-count');
                watched_count.html(parseInt(watched_count.html())+1);
                btn.toggleClass('btn-watched btn-not-watched');
                btn.attr('data-toggle', 'dropdown');
            },
            always: function(){
                btn.button('reset');
            }
        }
    );
});


$('.season-episodes').on('click', '.watched-episode', function(event){
    $(this).blur();
    var btn = $(this);
    if (btn.attr("disabled")) {
        return false;
    }
    var watched_count = btn.parent().parent().find('.btn-watched-count');
    var todo = btn.attr('do');
    if ((todo == 'decr') && (parseInt(watched_count.html()) <= 1)) {
        todo = 'delete'
    }
    btn.button('loading');
    api.post(
        '/api/watched',
        $.param({
            show_id: btn.attr('show-id'),
            number: btn.attr('episode-number'),
            do: todo,
        }),
        {
            done: function(){                
                var count = 0;
                if (btn.attr('do') == 'incr') {
                    count = parseInt(watched_count.html())+1;
                } else {
                    count = parseInt(watched_count.html())-1;               
                }
                watched_count.html(count);
                if (count <= 0) { 
                    var btn_watched = btn.parent().parent().find('.btn-watched');
                    btn_watched.toggleClass('btn-watched btn-not-watched');
                    btn_watched.attr('data-toggle', '');
                }
            },
            always: function(){
                btn.button('reset');
            }
        }
    );
});