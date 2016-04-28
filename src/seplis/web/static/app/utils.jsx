
export function isAuthed() {
    return (localStorage.getItem('access_token') !== null);
}

export function getUserId() {
    return localStorage.getItem('user_id');
}