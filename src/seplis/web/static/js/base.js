$(function(){
    $('.autocomplete').autocomplete({
        serviceUrl: '/api/suggest',   
        paramName: 'q',
        noCache: true,
        width: 400,
        transformResult: function(response) {
            response = $.parseJSON(response);
            return {
                suggestions: $.map(response, function(r) {
                    return { 
                        value: r.title.toString(), 
                        data: r,
                    };
                })
            };
        },
        formatResult: function (suggestion, currentValue) {
            return _.template(multiline(function(){/*
                <span class="title"><%- title %></span>
            */}),
                suggestion.data 
            );
        },    
        onSelect: function (suggestion) {
            location.href = '/show/'+suggestion.data.id;
        }
    });
    $('.change-page').change(function(){
        var url = $.url(location.href);
        p = url.param();
        p['page'] = $(this).val();
        location.href = url.attr('path') + '?' + $.param(p);
    });
});