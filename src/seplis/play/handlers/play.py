import logging, os
import asyncio
from sqlalchemy import select
from tornado import web, ioloop

from seplis.play.connections import database

from .types import pipe, hls
from ua_parser import user_agent_parser

from seplis import config, utils
from seplis.play import models

class Play_handler(web.RequestHandler):

    async def get(self):
        self._auto_finish = False
        self.ioloop = ioloop.IOLoop.current()
        self.agent = user_agent_parser.Parse(self.request.headers['User-Agent'])
        metadata = await get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.set_header('Content-Type', 'application/json')
            self.write('{"error": "No episode found"}')
            self.finish()
            return
        settings = get_device_settings(self)
        if settings['type'] == 'pipe':
            pipe.start(self, settings, metadata[0])
        if settings['type'] == 'hls':
            hls.start(self, settings, metadata[0])

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

    async def get(self):
        metadata = await get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No movie/episode found"}')
            return
        self.write(utils.json_dumps(metadata))

    def options(self, *args, **kwargs):
        self.set_status(204)

    def set_default_headers(self):
        set_header(self)
        self.set_header('Content-Type', 'application/json')

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
        device = 'default'
    logging.debug('Device: {}'.format(device))
    settings = device_settings.get(device)
    if not settings:
        raise web.HTTPError(400, 'Device: {} not supported'.format(
            device
        ))
    return settings

async def get_metadata(play_id):
    data = decode_play_id(play_id)
    async with database.session_async() as session:
        if data['type'] == 'series':
            query = select(models.Episode.meta_data).where(
                models.Episode.show_id == data['show_id'],
                models.Episode.number == data['number'],
            )
            files = await session.scalars(query)
            files = files.all()
            return files if files else None
        elif data['type'] == 'movie':
            query = select(models.Movie.meta_data).where(
                models.Movie.movie_id == data['movie_id'],
            )
            files = await session.scalars(query)
            files = files.all()
            return files if files else None

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
    'default': {
        'codec_names': [
            'h264',
        ],
        'pixel_formats': [
            'yuv420p',
        ],
        'transcode_codec': 'libx264',
        'transcode_pixel_format': 'yuv420p',
        'type': 'hls',
        'audio_channels_fix': True,
    },
    'hls.js': {
        'codec_names': [
            'h264',
        ],
        'pixel_formats': [
            'yuv420p',
        ],
        'transcode_codec': 'libx264',
        'transcode_pixel_format': 'yuv420p',
        'audio_channels_fix': True,
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
        'audio_channels': '2',
        'type': 'pipe',
    },
}