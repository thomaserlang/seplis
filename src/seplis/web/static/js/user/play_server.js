$(function(){
    $('#form-play-server').submit(function(event){
        event.preventDefault();
        var btn = $(this).find('button');
        btn.button('loading');
        api.post(
            '/api/user/play-server',
            $(this).serialize(),
            {
                done: function(data){
                    location.href = '/user/play-servers';
                },
                always: function(){
                    btn.button('reset');
                }
            }
        )
    });
    $('#button-play-server-delete').click(function(event){
        event.preventDefault();
        if (!confirm('Sure you wan\'t to delete this play server?')) {
            return;
        }
        var btn = $(this);
        btn.button('loading');
        api.delete(
            '/api/user/play-server',
            {
                'id': $(this).attr('play-server-id')
            },
            {
                done: function(data){
                    location.href = '/user/play-servers';
                },
                always: function(){
                    btn.button('reset');
                }
            }
        )
    });
});