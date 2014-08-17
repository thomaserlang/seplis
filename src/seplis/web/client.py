import logging
from tornado import httpclient, gen, ioloop, web
from seplis import utils

class Async_client(object):

    def __init__(self, url, client_id, client_secret=None, io_loop=None):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self._client = httpclient.AsyncHTTPClient(self.io_loop)
        self.access_token = None

    @gen.coroutine
    def _fetch(self, method, uri, body=None, headers=None):
        if not headers:
            headers = {}
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        if ('Authorization' not in headers) and self.access_token:
            headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        try:
            response = yield self._client.fetch(httpclient.HTTPRequest(
                self.url + uri, 
                method=method,
                body=utils.json_dumps(body) if body or {} == body else None, 
                headers=headers,
            ))
        except httpclient.HTTPError as e:
            response = e.response
            if not response and (e.code == 599):
                raise Api_error(
                    status_code=e.code,
                    code=e.code,
                    message='Timeout',
                )
        data = None
        if response.body:
            data = utils.json_loads(response.body.decode('utf-8'))
            if 400 <= response.code <= 600:
                raise Api_error(status_code=response.code, **data)
        raise gen.Return(data)

    @gen.coroutine
    def get(self, uri, headers=None):
        r = yield self._fetch('GET', uri, headers=headers)
        raise gen.Return(r)

    @gen.coroutine
    def delete(self, uri, headers=None):
        r = yield self._fetch('DELETE', uri, headers=headers)
        raise gen.Return(r)

    @gen.coroutine
    def post(self, uri, body={}, headers=None):
        r = yield self._fetch('POST', uri, body, headers=headers)
        raise gen.Return(r)

    @gen.coroutine
    def put(self, uri, body={}, headers=None):
        r = yield self._fetch('PUT', uri, body, headers=headers)
        raise gen.Return(r)

class Api_error(web.HTTPError):

    def __init__(self, status_code, code, message, errors=None, extra=None):
        web.HTTPError.__init__(self, status_code, message)
        self.status_code = status_code
        self.code = code
        self.errors = errors
        self.message = message
        self.extra = extra