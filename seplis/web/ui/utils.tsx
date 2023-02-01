import { IEpisode, ISeries } from './interfaces/series';

export function isAuthed() {
    return (localStorage.getItem('accessToken') !== null);
}

export function requireAuthed() {
    if (!isAuthed()) {
        location.href = '/sign-in';
        throw 'Not authed!';
    }
    return true;
}

export function getUserId() {
    requireAuthed();
    return localStorage.getItem('user_id') || 0;
}

export function getUserLevel() {
    return localStorage.getItem('user_level') || null;
}

export function pad(str: string | number, max: number): string {
    str = str.toString();
    return str.length < max ? pad("0" + str, max) : str;
}

export function episodeNumber(series: ISeries, episode: IEpisode) {
    let type = series.episode_type
    if (type == 2) {
        if (!episode.season || !episode.episode)
            type = 1
    } else if (type == 3) {
        if (!episode.air_date)
            type = 1
    }
    switch (type) {
        case 1: return`Episode ${episode.number}`; break;
        case 2: return`S${pad(episode.season,2)} · E${pad(episode.episode, 2)}`; break;
        case 3: return`Airdate: ${episode.air_date}`; break;
    }
}

export function episodeTitle(series: ISeries, episode: IEpisode) {
    let type = series.episode_type
    if (type == 2) {
        if (!episode.season || !episode.episode)
            type = 1
    } else if (type == 3) {
        if (!episode.air_date)
            type = 1
    }
    switch (type) {
        case 1: return`${episode.number}: ${episode.title}`; break;
        case 2: return`S${pad(episode.season,2)}E${pad(episode.episode, 2)}: ${episode.title}`; break;
        case 3: return`${episode.air_date}: ${episode.title}`; break;
    }
}

export function guid() {
    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
}

export function secondsToTime(secs: number) {
    const hours = Math.floor(secs / 3600);
    const minutes = Math.floor((secs - (hours * 3600)) / 60);
    const seconds = Math.floor(secs - (hours * 3600) - (minutes * 60));
    let hoursStr = ''
    let minutesStr = ''
    let secondsStr = ''
    if (hours < 10) 
        hoursStr = "0"+hours;
    if (minutes < 10) 
        minutesStr = "0"+minutes;
    if (seconds < 10)
        secondsStr = "0"+seconds;
    return (hours>0?hoursStr+':':'')+minutesStr+':'+secondsStr;
}

export function dateInDays(dt: Date | string) {
    if (typeof(dt) == "string") {
        dt = new Date(dt);
    }
    let seconds = Math.abs(dt.getTime()-new Date().getTime())/1000;
    let minutes, hours, days;
    let l = [];
    [minutes, seconds] = divmod(seconds, 60);
    [hours, minutes] = divmod(minutes, 60);
    [days, hours] = divmod(hours, 24);
    if (days > 0) l.push(pluralize(days, 'day'));
    if (hours > 0) l.push(pluralize(hours, 'hour'));
    if ((minutes > 0) && (hours < 1) && (days < 1)) 
        l.push(pluralize(minutes, 'minute'));
    return l.join(' ');
}

export function secondsToPretty(seconds: number, showTotalHours: boolean) {
    let totalHours = Math.round((((seconds/60)/60)*10))/10;
    if (seconds < 60) return pluralize(seconds, 'second');
    let minutes, hours, days, months, years;
    [minutes, seconds] = divmod(seconds, 60);
    [hours, minutes] = divmod(minutes, 60);
    [days, hours] = divmod(hours, 24);
    [months, days] = divmod(days, 30.42);
    [years, months] = divmod(months, 12);
    let l = [];
    if (years > 0) l.push(pluralize(Math.round(years), 'year'));
    if (months > 0) l.push(pluralize(Math.round(months), 'month'));
    if (days > 0) l.push(pluralize(Math.round(days), 'day'));
    if (hours > 0) l.push(pluralize(Math.round(hours), 'hour'));
    if (minutes > 0) l.push(pluralize(Math.round(minutes), 'minute'));
    let r = l.join(', ');
    if ((showTotalHours) && (totalHours >= 24)) {
        let h = pluralize(totalHours, 'hour');
        r = r + ` (${h})`;
    }
    return r;
}

export function pluralize(num: number, word: string) {
    if (num != 1) word = word + 's';
    return `${num} ${word}`
}

export function divmod(a: number, b: number) {
    return [Math.floor(a / b), a % b];
}

export function setTitle(title: string) {
    document.title = `${title} | SEPLIS`
}

export function secondsToHourMin(minutes: number) {
    if (!minutes)
        return
    const hours = Math.floor(minutes / 60)
    const minutesLeft = minutes % 60
    let s = ''
    if (hours > 0)
        s += `${hours}h`
    if (minutes > 0)
        s += ` ${minutesLeft}m`
    return s.trim()
}

export function langCodeToLang(code: string) {
    return new Intl.DisplayNames(['en'], { type: 'language' }).of(code)
}