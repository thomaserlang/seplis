
export function isAuthed() {
    return (localStorage.getItem('access_token') !== null);
}

export function requireAuthed() {
    if (!isAuthed()) {
        location.href = '/sign-in';
        throw 'Not authed!';
    }
    return true;
}

export function getUserId() {
    return localStorage.getItem('user_id') || 0;
}

export function getUserLevel() {
    return localStorage.getItem('user_level') || null;
}

export function pad (str, max) {
  str = str.toString();
  return str.length < max ? pad("0" + str, max) : str;
}

export function episodeTitle(show, episode) {
    switch (show.episode_type) {
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

export function secondsToTime(secs) {
    let hours = Math.floor(secs / 3600);
    let minutes = Math.floor((secs - (hours * 3600)) / 60);
    let seconds = secs - (hours * 3600) - (minutes * 60);

    if (hours < 10) 
        hours = "0"+hours;
    if (minutes < 10) 
        minutes = "0"+minutes;
    if (seconds < 10)
        seconds = "0"+seconds;
    return (hours>0?hours+':':'')+minutes+':'+Math.round(seconds);
}