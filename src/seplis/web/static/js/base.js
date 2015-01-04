String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

$(function(){
    $('.autocomplete').autocomplete({
        serviceUrl: '/api/suggest',   
        paramName: 'q',
        noCache: true,
        width: 400,
        triggerSelectOnValidInput: false,
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
                '<div class="show-suggest">'+
                '<span class="image"><img src="<% if (poster_image && poster_image.url) { %><%= poster_image.url %>@SX60<% } %>" width="60"></span>'+
                '<span class="text"><strong><%- title %></strong> '+
                    '<% if (premiered) { %>'+
                        '(<%- premiered.substring(0, 4) %>)'+
                    '<% } %>' +
                '</span>'+
                '</div>',
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
    $(document).on("hidden.bs.modal", '#seplis-modal', function (e) {
        var obj = $(e.target).removeData("bs.modal").find(".modal-content");

        obj.empty();
    });
});