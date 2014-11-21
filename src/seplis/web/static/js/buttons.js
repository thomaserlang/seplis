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

$('.season-episodes').on('click', '.not-watched', function(event){
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
                var watched_count = btn.parent().find('.times-watched');
                watched_count.html(parseInt(watched_count.html())+1);
                btn.toggleClass('watched not-watched');
                btn.attr('data-toggle', 'dropdown');
            },
            always: function(){
                btn.button('reset');
            }
        }
    );
});

$('.season-episodes').on('click', '.watched-button', function(event){
    $(this).blur();
    var btn = $(this);
    if (btn.attr("disabled")) {
        return false;
    }
    var watched_count = btn.parent().parent().find('.times-watched');
    var todo = btn.attr('do');
    if ((todo == 'decr') && (parseInt(watched_count.html()) <= 1)) {
        todo = 'delete';
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
                    var btn_watched = btn.parent().parent().find('.watched');
                    btn_watched.toggleClass('watched not-watched');
                    btn_watched.attr('data-toggle', '');
                }
            },
            always: function(){
                btn.button('reset');
            }
        }
    );
});

$('#form-multi-watched').submit(function(event){
    event.preventDefault();
    var btn = $(this).find('.btn');
    btn.button('loading');
    api.post(
        '/api/watched',
        $(this).serialize(),
        {
            done: function(data) {
                location.reload();
            },
            always: function(data){
                btn.button('reset');
            }
        }
    )
});

$('#button-multi-watched').click(function(){
    setTimeout(function(){
        $('#form-from-episode-number').focus();
    }, 10);
});