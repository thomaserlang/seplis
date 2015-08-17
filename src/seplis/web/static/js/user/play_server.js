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
                            '>'+
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
    $('#playserver-autocomplete-user').autocomplete({
        serviceUrl: '/api/users',   
        paramName: 'q',
        noCache: true,
        width: 200,
        triggerSelectOnValidInput: false,
        transformResult: function(response) {
            response = $.parseJSON(response);
            return {
                suggestions: $.map(response, function(r) {
                    return { 
                        value: r.name.toString(), 
                        data: r,
                    };
                })
            };
        },
        formatResult: function (suggestion, currentValue) {
            return _.template(
                '<div class="user-suggest">'+
                    '<span class="text">'+
                        '<%- name %>'+
                    '</span>'+
                '</div>',
                suggestion.data 
            );
        },    
        onSelect: function (data) {
            api.post(
                '/api/user/play-server/user', 
                {
                    'server_id': $('#playserver-autocomplete-user')
                        .attr('server-id'),
                    'user_id': data.data.id
                },
                {
                    done: function(data) {
                        location.reload();
                    }
                }
            );
        }
    });
    $('.play-server-remove-user').click(function(){
        api.delete(
            '/api/user/play-server/user',
            {
                'user_id': $(this).attr('user-id'),
                'server_id': $(this).attr('server-id')
            },
            {
                done: function() {
                    location.reload();
                }
            }
        );
    });
});