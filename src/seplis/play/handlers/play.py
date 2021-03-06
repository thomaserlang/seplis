import logging, os
import asyncio
from tornado import web, ioloop

from .types import pipe, hls
from ua_parser import user_agent_parser

from seplis import config, utils
from seplis.play.decorators import new_session
from seplis.play import models

class Play_handler(web.RequestHandler):

    def get(self):
        self._auto_finish = False
        self.ioloop = ioloop.IOLoop.current()
        self.agent = user_agent_parser.Parse(self.request.headers['User-Agent'])
        metadata = get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No episode found"}')
            self.finish()
            return
        settings = get_device_settings(self)
        if settings['type'] == 'pipe':
            pipe.start(self, settings, metadata)
        if settings['type'] == 'hls':
            hls.start(self, settings, metadata)

    def set_default_headers(self):
        set_header(self)

    def on_connection_close(self):
        if hasattr(self, 'event_connection_close'):
            self.event_connection_close()

    def options(self, *args, **kwargs):
        self.set_status(204)

class File_handler(web.StaticFileHandler):

    def set_default_headers(self):
        set_header(self)

    def should_return_304(self):
        return False

class Metadata_handler(web.RequestHandler):

    def get(self):
        metadata = get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No episode found"}')
            return
        self.write(metadata)

    def options(self, *args, **kwargs):
        self.set_status(204)

    def set_default_headers(self):
        set_header(self)

def set_header(self):
    self.set_header('Cache-Control', 'no-cache, must-revalidate')
    self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Access-Control-Allow-Headers', 'User-Agent, Content-Type')
    self.set_header('Access-Control-Allow-Methods', 'GET')
    self.set_header('Access-Control-Expose-Headers', 'Content-Type')

def get_device_settings(handler):
    device = handler.get_argument('device', None)
    if not device:
        device = handler.agent['user_agent']['family']
    logging.debug('Device: {}'.format(device))
    settings = device_settings.get(device)
    if not settings:
        raise web.HTTPError(400, 'Device: {} not supported'.format(
            device
        ))
    return settings

def get_metadata(play_id):
    data = decode_play_id(play_id)
    with new_session() as session:
        episode = session.query(
            models.Episode.meta_data,
        ).filter(
            models.Episode.show_id == data['show_id'],
            models.Episode.number == data['number'],
        ).first()
        return episode.meta_data if episode else None

def decode_play_id(play_id):
    data = web.decode_signed_value(
        secret=config['play']['secret'],
        name='play_id',
        value=play_id,
        max_age_days=0.3,
    )
    if not data:
        raise web.HTTPError(400, 'Play id invalid')
    return utils.json_loads(data)

device_settings = {
    'hls': {
        'codec_names': [
            'h264',
        ],
        'pixel_formats': [
            'yuv420p',
        ],
        'transcode_codec': 'libx264',
        'transcode_pixel_format': 'yuv420p',
        'type': 'hls',
    },
    'chromecast': {
        'codec_names': [
            'h264',
        ],
        'pixel_formats': [
            'yuv420p',
        ],
        'transcode_codec': 'libx264',
        'transcode_pixel_format': 'yuv420p',
        'type': 'pipe',
    },
    'chrome': {
        'codec_names': [
            'h264',
        ],
        'pixel_formats': [
            'yuv420p',
        ],
        'transcode_codec': 'libx264',
        'transcode_pixel_format': 'yuv420p',
        'type': 'pipe',
    },
}