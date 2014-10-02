$(function(){
    $('#select-fan-of-pages').change(function(){
        var url = $.url(location.href);
        p = url.param();
        p['page'] = $(this).val();
        location.href = url.attr('path') + '?' + $.param(p);
    });
});