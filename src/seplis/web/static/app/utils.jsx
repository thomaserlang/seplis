
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