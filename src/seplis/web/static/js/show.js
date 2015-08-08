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
    $('.play-next-button').click(function(){
        var show_id = $(this).attr('show-id');
        api.get('/api/show-play-next', {'show_id': show_id}, {
            done: function(episode){
                location.href = '/show/'+show_id+
                    '/episode/'+episode.number.toString()+'/play';
            }
        });
    });
});

function get_show_play_next(show_id) {
    $('#show-play-next-image')
        .attr('data-target', '')
        .attr('href', '');
    api.get('/api/show-play-next', {'show_id': show_id}, {
        done: function(episode){
            $('#show-play-next-image')
                .attr('data-target', '#seplis-modal')
                .attr(
                    'href', 
                    '/modal/play-episode?show_id='+show_id+
                    '&episode_number='+episode.number
                );
        }
    })
}