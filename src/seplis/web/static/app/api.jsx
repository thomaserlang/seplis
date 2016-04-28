import $ from 'jquery';

function handleError(error) {
    if (error.status === 401) {
        if (error.responseJSON.code === 1009) {
            localStorage.removeItem('access_token');
            location.href = '/sign-in';
        }
    }
}

export var apiClientSettings = {
    'baseUrl': '',
};

export function request(url, options = {}) {
    let query = $.param(options.query || '', true);
    let method = options.method || (options.data ? 'POST':'GET');
    let data = options.data;

    if (typeof data !== 'undefined' && method !== 'GET') {
        data = JSON.stringify(data);
    }
    
    if (!url.startsWith('http')) {
        url = apiClientSettings.baseUrl + url;
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

    return $.ajax({
        url: url,
        method: method,
        data: data,
        contentType: 'application/json',
        headers: headers,
        'error': handleError,
    })
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : null;
}