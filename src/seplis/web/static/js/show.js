$(function(){
    $('#form-new-show').submit(function(event){
        event.preventDefault();
        api.post(
            '/api/show-new',
            $(this).serialize(),
            {
                done: function(data){
                    location.href = '/show/'+data['id'];
                }
            }
        )
    });
    $('#form-edit-show').submit(function(event){
        event.preventDefault();
        api.post(
            '/api/show-edit/'+$(this).attr('show-id'),
            $(this).serialize(),
            {
                done: function(data){                    
                    $.growl({ 
                        title: "Success!", 
                        message: "The show has been updated.",
                        location: 'tc',
                    });
                }
            }
        )
    });
    $('#form-edit-show #imdb, #form-new-show #imdb').on('paste', function(){
        var obj = $(this);
        setTimeout(function () { 
            $.getJSON('http://api.tvmaze.com/lookup/shows', {'imdb': obj.val()}, function(show){
                show.externals['tvmaze'] = show.id;
                $('#form-edit-show .input-external-id, #form-new-show .input-external-id').each(function(){
                    if ($(this).val() != '')
                        return;
                    if (this.name in show.externals)
                        $(this).val(show.externals[this.name]);
                });
            });
        }, 10);
    });
    $('#show-select-index-sources select').change(function(){
        var val = $(this).val();
        $('#show-select-index-sources select').each(function(){
            if ($(this).val() != '')
                return;
            $(this).val(val);            
        });
    });

    if ($('#alternative-titles').length) {
        $('#alternative-titles').select2({
            tags: []
        });
    }

    $('date.show-date').each(function(){
        var hours = moment.utc(
            $(this).attr('title'), 
            moment.iso_8601
        ).diff(
            moment.utc(),
            'hours'
        );
        if (hours < 0) {
            hours = 0;
        } 
        else if (hours > 0 && hours < 24){
            hours = 24
        }
        var days = (hours / 24).toString();
        if (days == '0') {
            days = 'Today';
        } 
        else if (days == '1') {
            days = 'Tomorrow'
        } else {
            days = 'in '+Math.ceil(days)+' days';
        }
        $(this).text(days);
    });
    $('.season-select select').change(function(){
        location.href = '/show/'+$(this).attr('show-id')+'?season='+$(this).val();
    });
    $('.show-info .description .description-text').dotdotdot({
        after: "a.readmore",
        tolerance: 0,
        height: 70
    });
    $('.dropdown-form').click(function(e) {
        e.stopPropagation();
    });
    $('.show-list-description-text').dotdotdot({
        after: "a.readmore",
        tolerance: 0,
        height: 40
    });
    $('.play-next').click(function(){
        var show_id = $(this).attr('show-id');
        api.get('/api/show-play-next', {'show_id': show_id}, {
            done: function(episode){
                location.href = '/show/'+show_id+
                    '/episode/'+episode.number.toString()+'/play';
            }
        });
    });
    $('.play-next-button').on('touchstart', function(e){
        e.preventDefault();
    });

    $('.show-list-image-tooltip').qtip({
        content: {
            text: function(event, api) {
                return $(this).find('.show-tooltip-text').html();
            },
            button: true,
        },
        hide: { 
            delay: isMobile() ? 0 : 250, 
            fixed: true,
            effect: false,
        },
        show: {
            effect: false,
            delay: isMobile() ? 0 : 500,
        },
        position: {
            adjust: {
                method: 'flip shift'
            },
            viewport: $(window),
            at: 'center right',
            my: 'left center',
        },
        style: { 
            classes: 'show-tooltip',
            def: false,
            tip: { 
                width: 15, 
                offset: -50,
            },
        },
    });
});