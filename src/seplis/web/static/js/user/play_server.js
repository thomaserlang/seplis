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
    $('.episode-play-servers').click(function(){
        var menu = $(this).parent().find('.dropdown-menu');
        api.get(
            '/api/show-episode/play-servers',
            {
                'show_id': $(this).attr('show-id'),
                'episode_number': $(this).attr('episode-number'),
            },
            {
                done: function(data){
                    menu.html(_.template(
                        '<% for (var ps in play_servers) { %>'+
                            '<li>'+
                            '<a '+
                                'href="/play-episode?play_server_id=<%- play_servers[ps].play_server.id %>&play_id=<%- play_servers[ps].play_id %>"'+
                            '>'
                                '<%- play_servers[ps].play_server.name %>'+
                            '</a>'+
                            '</li>'+
                        '<% } %>',
                        {'play_servers': data}
                    ));
                },
            }
        )
    });
});