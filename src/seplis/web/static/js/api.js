function Api_error(status_code, code, errors, message, extra) {
    this.status_code = status_code;
    this.code = code;
    this.errors = errors;
    this.message = message;
    this.extra = extra;
}

Api_error.prototype.toString(function(){
    return this.message + '('+status_code+')';
});

function Api() {
    this.defaultErrorCallback = null;
    this.defaultDoneCallback = null;
    this.defaultAlwaysCallback = null;
    this.loaderGif = null;
}

Api.prototype._method = function(url, method, data, callbacks){
    var _callbacks = {
        done: this.defaultDoneCallback,
        error: this.defaultErrorCallback,
        always: this.defaultAlwaysCallback,
    }
    if (typeof(callbacks) !== 'undefined') {
        $.extend(_callbacks, callbacks);
    }
    headers = {
        'X-XSRFToken': getCookie('_xsrf')
    }
    if (this.loaderGif !== null) {
        $('.api_request_loader').html('<img src="'+this.loaderGif+'" />');
    }
    $.ajax({
        url: url,
        type: method,
        data: data,
        headers: headers
    }).error(function(obj, text_status){
        if ((obj.status >= 400) && (obj.status <= 600)) {
            error = new Api_error(
                obj.status, 
                obj.responseJSON.code,
                obj.responseJSON.errors,
                obj.responseJSON.message,
                obj.responseJSON.extra
            )
        } else {
            error = new Api_error(
                null,
                null,
                null,
                'can\'t access the seplis api server',
                null
            );
        }
        if (_callbacks.error !== null) {
            _callbacks.error(error);
        }
    }).done(function(data){
        if (_callbacks.done !== null) {
            _callbacks.done(data);
        }
    }).always(function(){
        if (this.loaderGif !== null) {
            $('.api_request_loader').empty();
        }
        if (_callbacks.always !== null) {
            _callbacks.always(data);
        }
    });
}

Api.prototype.post = function(url, data, callbacks) {
    this._method(url, 'POST', data, callbacks);
}

Api.prototype.get = function(url, data, callbacks) {
    this._method(url, 'GET', data, callbacks);
}

Api.prototype.delete = function(url, data, callbacks) {
    this._method(url, 'DELETE', data, callbacks);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    if (!r && name == "_xsrf"){
        return 'not_found'
    }
    return r ? r[1] : undefined;
}