export const EVENT_EPISODE_WATCHED_STATUS = 'episode_watched_status';
/**
 * @param {string} method - incr or decr
 * @param {int} movieId
 * @param {int} episode_number
 */
export function trigger_episode_watched_status(method, show_id, episode_number) {
    let event = new Event(EVENT_EPISODE_WATCHED_STATUS, {
        method: method,
        show_id: show_id,
        episode_number: episode_number,
    });
    document.dispatchEvent(event);
}

export const EVENT_MOVIE_WATCHED_STATUS = 'episode_watched_status';
/**
 * @param {string} method - incr or decr
 * @param {int} movieId
 */
export function trigger_movie_watched_status(method, movieId) {
    let event = new Event(EVENT_MOVIE_WATCHED_STATUS, {
        method: method,
        movieId: movieId,
    });
    document.dispatchEvent(event);
}