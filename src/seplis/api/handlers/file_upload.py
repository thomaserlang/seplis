from urllib.parse import urljoin
from tornado import httpclient
from seplis.api.handlers import base
from seplis import config, utils
from io import BytesIO

class Handler(base.Handler):

    def get_httpclient(self):
        return httpclient.AsyncHTTPClient()

    async def save_files(self):
        files = []
        if not self.request.files:
            return
        for key in self.request.files:
            for file_ in self.request.files[key]:
                files.append(
                    ('image', file_['filename'], file_['body'])
                )
        content_type, body = utils.MultipartFormdataEncoder().encode([], files)
        client = self.get_httpclient()
        response = await client.fetch(
            urljoin(config['api']['storitch'], 'store'),
            method='POST',
            headers={'Content-Type': content_type},
            body=body,
        )  
        return utils.json_loads(response.body)

