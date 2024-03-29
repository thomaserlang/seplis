import dayjs from 'dayjs'
import { IEpisode } from '../interfaces/episode'


export function isAuthed() {
    return (localStorage.getItem('accessToken') !== null)
}


export function requireAuthed() {
    if (!isAuthed()) {
        location.href = '/sign-in'
        throw 'Not authed!'
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
    str = str.toString()
    return str.length < max ? pad("0" + str, max) : str
}


export function episodeNumber(episode: IEpisode) {
    if (!episode)
        return null
    if (!episode.season || !episode.episode)
        return `Episode ${episode.number}`
    
    if (episode.episode != episode.number)
        return `S${pad(episode.season,2)}E${pad(episode.episode, 2)} (${episode.number})`

    return `S${pad(episode.season,2)}E${pad(episode.episode, 2)}`
}


export function episodeTitle(episode: IEpisode) {
    return `${episodeNumber(episode)}: ${episode.title}`
}


export function EpisodeAirdate(episode: IEpisode) {
    if (episode.air_datetime)
        return <span title={episode.air_datetime}>{dayjs(episode.air_datetime).format('YYYY-MM-DD')}</span>
    return episode.air_date || 'Unknown airdate'
}


export function EpisodeAirdatetime(episode: IEpisode) {
    if (episode.air_datetime)
        return <span title={episode.air_datetime}>{dayjs(episode.air_datetime).format('YYYY-MM-DD HH:mm')}</span>
    return 'Unknown airdate'
}


export function secondsToTime(secs: number) {
    const hours = Math.floor(secs / 3600);
    const minutes = Math.floor((secs - (hours * 3600)) / 60);
    const seconds = Math.floor(secs - (hours * 3600) - (minutes * 60));
    
    return (hours>0?pad(hours, 2)+':':'')+pad(minutes, 2)+':'+pad(seconds, 2);
}


export function dateInDays(dt: Date | string) {
    if (typeof(dt) == "string")
        dt = new Date(dt)
    let seconds = Math.abs(dt.getTime()-new Date().getTime())/1000
    let minutes, hours, days
    let l = [];
    [minutes, seconds] = divmod(seconds, 60);
    [hours, minutes] = divmod(minutes, 60);
    [days, hours] = divmod(hours, 24);
    if (days > 0) l.push(pluralize(days, 'day'))
    if (hours > 0) l.push(pluralize(hours, 'hour'))
    if ((minutes > 0) && (hours < 1) && (days < 1)) 
        l.push(pluralize(minutes, 'minute'))
    return l.join(' ')
}


export function dateCountdown(dt: string) {
    const m = (new Date(dt).getTime() - new Date().getTime())
    if (m > 0)
        return <>in <span title={dt}>{dateInDays(dt)}</span></>
    return <><span title={dt}>{dateInDays(dt)}</span> ago</>
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
    if (minutesLeft > 0)
        s += ` ${minutesLeft}m`
    return s.trim()
}


export function langCodeToLang(code: string) {
    try {
        return new Intl.DisplayNames(['en'], { type: 'language' }).of(code)
    } catch (e) {
        return code
    }
}


export function removeEmpty(obj: Object) {
    return Object.entries(obj)
      .filter(([_, v]) => (v != null) && (v != '') && (v != 0))
      .reduce((acc, [k, v]) => ({ ...acc, [k]: v }), {});
}