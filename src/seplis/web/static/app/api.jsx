import $ from 'jquery';

export function request(url, options = {}) {
    let query = $.param(options.query || '', true);
    let method = options.method || (options.data ? 'POST':'GET');
    let data = options.data;

    if (typeof data !== 'undefined' && method !== 'GET') {
        data = JSON.stringify(data);
    }

    if (query) {
        if (url.indexOf('?') === -1) {
            url += '?' + query;
        } else {
            url += '&' + query;
        }
    }

    let headers = {
        'Accept': 'application/json; charset=utf-8',
    }
    if (method !== 'GET') {
        headers['X-XSRFToken'] = getCookie('_xsrf');
    }

    return $.ajax({
        url: url,
        method: method,
        data: data,
        contentType: 'application/json',
        headers: headers,
        success: options.success,
        error: options.error,
        complete: options.complete,
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : null;
}