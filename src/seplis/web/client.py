import logging
import json
from tornado import httpclient, gen, ioloop, web
from urllib.parse import urljoin, urlencode
from seplis import utils
from functools import partial

TIMEOUT = 60 # seconds

class HTTPData(object):

    def __init__(self, client, response, timeout=TIMEOUT):
        self.client = client
        self.data = utils.json_loads(response.body) if \
            response and response.body \
                else None
        self.timeout = timeout
        self.link = {}
        self.next = None
        self.prev = None
        self.first = None
        self.last = None
        self.count = None
        self.pages = None

        if not response:
            return
        links = {}
        if 'Link' in response.headers:
            links = utils.parse_link_header(
                response.headers['Link']
            )
        self.next = links.get('next')
        self.prev = links.get('prev')
        self.first = links.get('first')
        self.last = links.get('last')
        if 'X-Total-Count' in response.headers:
            self.count = int(response.headers['X-Total-Count'])
        if 'X-Total-Pages' in response.headers:
            self.pages = int(response.headers['X-Total-Pages'])

    def to_dict(self):
        return self.data

    def all(self):
        s = self
        while True:
            for d in s.data:
                yield d
            if not s.next:
                break
            s = s.client.get(s.next, timeout=self.timeout)

    @gen.coroutine
    def all_async(self):
        s = self
        data = []
        while True:
            for d in s.data:
                data.append(d)
            if not s.next:
                break
            s = yield s.client.get(s.next, timeout=self.timeout)
        return data

    def __iter__(self):
        for d in self.data:
            yield d

    def __str__(self):
        return utils.json_dumps(self.data)

    def __len__(self):
        if not self.data:
            return 0
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

class Async_client(object):

    def __init__(self, url, client_id=None, client_secret=None, 
                 access_token=None, version='1', io_loop=None):
        self.url = urljoin(url, str(version))
        self.client_id = client_id
        self.client_secret = client_secret
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self._client = httpclient.AsyncHTTPClient(self.io_loop)
        self.access_token = access_token

    @gen.coroutine
    def _fetch(self, method, uri, body=None, headers=None, timeout=TIMEOUT):
        if not headers:
            headers = {}
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        if 'Accept' not in headers:
            headers['Accept'] = 'application/json'
        if ('Authorization' not in headers) and self.access_token:
            headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        try:
            if uri.startswith('http'):
                url = uri
            else:
                if not uri.startswith('/'):
                    uri = '/'+uri
                url = self.url+uri
            response = yield self._client.fetch(httpclient.HTTPRequest(
                url, 
                method=method,
                body=utils.json_dumps(body) if body or {} == body else None, 
                headers=headers,
                connect_timeout=timeout,
                request_timeout=timeout,
            ))
        except httpclient.HTTPError as e:
            response = e.response
            if not response and (e.code == 599):
                raise API_error(
                    status_code=e.code,
                    code=e.code,
                    message='Timeout',
                )
        data = None
        if response.code != 404:
            if 400 <= response.code <= 600:
                if response.headers.get('Content-Type') == 'application/json':
                    data = utils.json_loads(response.body)
                    raise API_error(status_code=response.code, **data)
                raise Exception(response.body)
            data = HTTPData(self, response, timeout=timeout)
        if data is None:
            data = HTTPData(self, None, timeout=timeout)
        return data

    @gen.coroutine
    def get(self, uri, data=None, headers=None, timeout=TIMEOUT):     
        if data != None:
            if isinstance(data, dict):
                data = urlencode(data, True)
            uri += '{}{}'.format('&' if '?' in uri else '?', data)
        r = yield self._fetch(
            'GET', 
            uri, 
            headers=headers,
            timeout=timeout,
        )
        return r

    @gen.coroutine
    def delete(self, uri, headers=None, timeout=TIMEOUT):
        r = yield self._fetch(
            'DELETE', 
            uri, 
            headers=headers,
            timeout=timeout,
        )
        return r

    @gen.coroutine
    def post(self, uri, body={}, headers=None, timeout=TIMEOUT):
        r = yield self._fetch(
            'POST', 
            uri, 
            body, 
            headers=headers,
            timeout=timeout,
        )
        return r

    @gen.coroutine
    def put(self, uri, body={}, headers=None, timeout=TIMEOUT):
        r = yield self._fetch(
            'PUT', 
            uri, 
            body, 
            headers=headers,
            timeout=timeout,
        )
        return r

    @gen.coroutine
    def patch(self, uri, body={}, headers=None, timeout=TIMEOUT):
        r = yield self._fetch(
            'PATCH', 
            uri, 
            body, 
            headers=headers,
            timeout=timeout,
        )
        return r

class Client(Async_client):

    def get(self, uri, data=None, headers=None, timeout=TIMEOUT):
        return self.io_loop.run_sync(partial(
            Async_client.get, 
            self, 
            uri, 
            data=data, 
            headers=headers,
            timeout=timeout,
        ))    

    def delete(self, uri, headers=None, timeout=TIMEOUT):
        return self.io_loop.run_sync(partial(
            self._fetch, 
            'DELETE', 
            uri, 
            headers=headers,
            timeout=timeout,
        ))

    def post(self, uri, body={}, headers=None, timeout=TIMEOUT):
        return self.io_loop.run_sync(partial(
            self._fetch, 
            'POST', 
            uri, 
            body, 
            headers=headers,
            timeout=timeout,
        ))

    def put(self, uri, body={}, headers=None, timeout=TIMEOUT):
        return self.io_loop.run_sync(partial(
            self._fetch, 
            'PUT', 
            uri, 
            body, 
            headers=headers,
            timeout=timeout,
        ))

    def patch(self, uri, body={}, headers=None, timeout=TIMEOUT):
        return self.io_loop.run_sync(partial(
            self._fetch, 
            'PATCH', 
            uri, 
            body, 
            headers=headers,
            timeout=timeout,
        ))

class API_error(web.HTTPError):

    def __init__(self, status_code, code, message, errors=None, extra=None):
        web.HTTPError.__init__(self, status_code, message)
        self.status_code = status_code
        self.code = code
        self.errors = errors
        self.message = message
        self.extra = extra

    def __str__(self):
        result = '{} ({})'.format(self.message, self.code)
        if self.errors:
            result += '\n\nErrors:\n'
            result += json.dumps(
                self.errors,
                indent=4, 
                separators=(',', ': ')
            )
        if self.extra:
            result += '\n\nExtra:\n'
            result += json.dumps(
                self.extra,
                indent=4, 
                separators=(',', ': ')
            )
        return result
