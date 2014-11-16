String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

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
            return _.template(
                '<span class="title"><%- title %></span>',
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
    $('.change-layout').click(function(event){
        event.preventDefault();
        $.cookie('layout', $(this).attr('data-layout'), { expires: 1*365 });
        location.reload();
    });
});