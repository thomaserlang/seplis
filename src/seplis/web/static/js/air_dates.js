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
            moment(
                $(this).attr('title'), 
                moment.iso_8601
            ).calendar()
        );
    });
});