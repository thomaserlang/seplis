import logging
import tornado.web
import tornado.gen
import os
from .types import pipe, hls
from ua_parser import user_agent_parser

from seplis import config
from seplis.play.decorators import new_session
from seplis.play import models

class Play_handler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        self.ioloop = tornado.ioloop.IOLoop.current()
        with new_session() as session:
            episode = session.query(
                models.Episode.meta_data,
            ).filter(
                models.Episode.show_id == self.get_argument('show_id'),
                models.Episode.number == self.get_argument('number'),
            ).first()
            metadata = episode.meta_data

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

class File_handler(tornado.web.StaticFileHandler):

    def set_default_headers(self):
        set_header(self)

def set_header(self):
    self.set_header('Cache-Control', 'no-cache, must-revalidate')
    self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Access-Control-Allow-Headers', 'User-Agent')
    self.set_header('Access-Control-Allow-Methods', 'GET')
    self.set_header('Access-Control-Expose-Headers', 'Content-Type')

def get_device_settings(handler):
    device = handler.get_argument('device', None)
    if not device:
        agent = user_agent_parser.Parse(handler.request.headers['User-Agent'])
        device = agent['user_agent']['family']
    settings = device_settings.get(device)
    if not settings:
        raise tornado.web.HTTPError(400, 'Device: {} not supported'.format(
            agent['user_agent']['family']
        ))
    return settings

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