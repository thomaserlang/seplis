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
                $(_this).html('Fan');
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
                $(_this).html('Fan');
            }
        }
    );
});