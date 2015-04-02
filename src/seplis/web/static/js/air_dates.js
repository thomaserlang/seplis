$(function(){
    moment.locale('en', {
        calendar : {
            lastDay : '[Yesterday] (dddd)',
            sameDay : '[Today] (dddd)',
            nextDay : '[Tomorrow] (dddd)',
            lastWeek : '[Last] dddd',
            nextWeek : 'dddd',
            sameElse : 'dddd'
        }
    });
    $('.airdates date').each(function(){
        $(this).text(
            moment.utc(
                $(this).attr('title'), 
                moment.iso_8601
            ).calendar()
        );
    });
    $('.airdate-show-image').qtip({
        content: {
            text: function(event, api) {
                return $(this).find('.airdate-show-tooltip').html();
            },
            button: true,
        },
        hide: { 
            delay: isMobile() ? 0 : 250, 
            fixed: true,
            effect: false,
        },
        show: {
            effect: false,
            delay: isMobile() ? 0 : 500,
        },
        position: {
            adjust: {
                method: 'flip shift'
            },
            viewport: $(window),
            at: 'center right',
            my: 'left center',
        },
        style: { 
            classes: 'show-tooltip',
            def: false,
            tip: { 
                width: 15, 
                offset: -50,
            },
        },
    });
});