$(function(){
    $('#sign-in-form').submit(function(event){
        event.preventDefault();
        var btn = $(this).find('button');
        btn.button('loading')
        api.post(
            '/api/sign-in', 
            $(this).serialize(), 
            {
                done: function(data){
                    location.href = $('#next').val();
                },
                always: function(){
                    btn.button('reset')                
                }
            }
        );
    });
    
    $('#sign-up-form').submit(function(event){
        event.preventDefault();
        var btn = $(this).find('button');
        btn.button('loading')
        api.post(
            '/api/sign-up', 
            $(this).serialize(), 
            {
                done: function(data){
                    location.href = $('#next').val();
                },
                always: function(){
                    btn.button('reset')
                }
            }
        );
    });

    $('#change-password-form').submit(function(event){
        event.preventDefault();
        var btn = $(this).find('button');
        btn.button('loading')
        api.post(
            '/api/change-password', 
            $(this).serialize(), 
            {
                done: function(data){
                    location.href = '/';
                },
                always: function(){
                    btn.button('reset')
                }
            }
        );
    });
});
