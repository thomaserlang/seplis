import logging
import tornado.web
import tornado.gen
import os
from .types import pipe, hls
from ua_parser import user_agent_parser

from seplis import config, utils
from seplis.play.decorators import new_session
from seplis.play import models

class Play_handler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.agent = user_agent_parser.Parse(self.request.headers['User-Agent'])
        metadata = get_metadata(self.get_argument('play_id'))
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

    def options(self):
        pass

class File_handler(tornado.web.StaticFileHandler):

    def set_default_headers(self):
        set_header(self)

class Metadata_handler(tornado.web.RequestHandler):

    def get(self):
        metadata = get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No episode found"}')
            return
        self.write(metadata)

    def options(self):
        pass

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
    settings = device_settings.get(device)
    if not settings:
        raise tornado.web.HTTPError(400, 'Device: {} not supported'.format(
            agent['user_agent']['family']
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
        return episode.meta_data

def decode_play_id(play_id):
    return utils.json_loads(tornado.web.decode_signed_value(
        secret=config['play']['secret'],
        name='play_id',
        value=play_id,
        max_age_days=0.3,
    ))

device_settings = {
    'Other': {
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
    'Chrome': {
        'codec_names': [
            'h264',
            'webm',
        ],
        'pixel_formats': [
            'yuv420p',
        ],
        'transcode_codec': 'libx264',
        'transcode_pixel_format': 'yuv420p',
        'type': 'pipe',
    },
    'Mobile Safari': {
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
    'Chrome Mobile iOS': {
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
}