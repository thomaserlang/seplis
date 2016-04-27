
export function isAuthed() {
    return (localStorage.getItem('access_token') !== null);
}