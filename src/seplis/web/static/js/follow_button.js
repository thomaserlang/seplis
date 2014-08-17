$('.follow-button').on('click', '.btn-follow', function(event){
    $(this).blur();
    var _this = this;
    api.post(
        '/follow',
        $.param({
            show_id: $(_this).attr('show-id'),
            do: 'follow'
        }),
        {
            done: function(){
                var follow_count = $(_this).parent().find('.btn-follow-count');
                follow_count.html(parseInt(follow_count.html())+1);
                $(_this).toggleClass('btn-follow btn-unfollow');
                $(_this).html('Unfollow');
            }
        }
    );
});

$('.follow-button').on('click', '.btn-unfollow', function(event){
    $(this).blur();
    var _this = this;
    api.post(
        '/follow',
        $.param({
            show_id: $(_this).attr('show-id'),
            do: 'unfollow'
        }),
        {
            done: function(){
                var follow_count = $(_this).parent().find('.btn-follow-count');
                follow_count.html(parseInt(follow_count.html())-1);                
                $(_this).toggleClass('btn-unfollow btn-follow');
                $(_this).html('Follow');
            }
        }
    );
});