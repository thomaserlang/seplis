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
});
