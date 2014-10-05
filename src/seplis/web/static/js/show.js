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
    $('#alternative-titles').select2({tags:[]});

    $('.season-episodes .episode .next-episode date').each(function(){
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
            days = 'In '+Math.ceil(days)+' days';
        }
        $(this).text(
            days
        );
    });
    $('.season-select select').change(function(){
        location.href = '/show/'+$(this).attr('show-id')+'?season='+$(this).val();
    });
    $('.show-info .description .description-text').dotdotdot({
        after: "a.readmore",
        tolerance: 0,
        height:70,
    });
    $('.dropdown-form input, .dropdown-form label, .dropdown-form .btn').click(function(e) {
        e.stopPropagation();
    });
});
