
export function isAuthed() {
    return (localStorage.getItem('access_token') !== null);
}

export function getUserId() {
    return localStorage.getItem('user_id') || 0;
}

export function getUserLevel() {
    return localStorage.getItem('user_level') || null;
}