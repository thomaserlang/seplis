export const EVENT_EPISODE_WATCHED_STATUS = 'episode_watched_status';
/**
 * @param {string} method - incr or decr
 * @param {int} show_id
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