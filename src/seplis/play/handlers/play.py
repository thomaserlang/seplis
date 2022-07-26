import asyncio
import http
import logging
import mimetypes
from typing import List, Optional, Union
from aiofile import async_open
import os
from pydantic import BaseModel, conlist, constr
from sqlalchemy import select
from tornado import web, escape
from seplis.api import exceptions
from seplis.play.connections import database
from seplis.play.handlers.transcoders import dash, pipe
from seplis.play.handlers.transcoders.base import Transcoder
from .transcoders import hls
from seplis import config, utils
from seplis.play import models

from seplis.play.handlers import transcoders

class Transcode_setting_arguments(BaseModel):

    play_id: conlist(str, max_items=1)
    session: conlist(str, max_items=1)
    supported_pixel_formats: List[str]
    format: conlist(str, max_items=1)
    transcode_codec: conlist(str, max_items=1)
    transcode_pixel_format: conlist(str, max_items=1)

    start_time: Optional[conlist(Union[int, float, None], max_items=1)]
    audio_lang: Optional[conlist(Optional[str], max_items=1)]
    subtitle_lang: Optional[conlist(Optional[str], max_items=1)]
    audio_channels: Optional[conlist(Optional[int], max_items=1)]
    width: Optional[conlist(Optional[Union[int, constr(max_length=0)]], max_items=1)]
    audio_channels_fix: conlist(Optional[int], max_items=1) = [True]

class Base_handler(web.RequestHandler):

    def set_default_headers(self) -> None:
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'User-Agent, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Expose-Headers', 'Content-Type')

    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            if isinstance(kwargs['exc_info'][1], exceptions.API_exception):
                self.write_object({
                    'code': kwargs['exc_info'][1].code,
                    'message': kwargs['exc_info'][1].message,
                    'errors': kwargs['exc_info'][1].errors,
                    'extra': kwargs['exc_info'][1].extra,
                })
                return
        if 'exc_info' in kwargs and isinstance(kwargs['exc_info'][1], web.HTTPError) and kwargs['exc_info'][1].log_message:
            msg = kwargs['exc_info'][1].log_message
        else:
            msg = http.client.responses[status_code]
        self.write_object({
            'code': -1,
            'message': msg,
            'errors': None,
            'extra': None,
        })

    def write_object(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(
            utils.json_dumps(obj),
        )

    def options(self, *args, **kwargs):
        self.set_status(204)

class Transcode_handler(Base_handler):

    async def get(self):
        settings = self.parse_settings()
        metadata = await get_metadata(settings.play_id)
        if not metadata:
            self.set_status(404)
            self.write_object({"error": "No episode found"})
            return

        if settings.format == 'hls':
            self.set_header('Content-Type', 'application/vnd.apple.mpegurl')
            cls = hls.Hls_transcoder
        elif settings.format == 'dash':
            self.set_header('Content-Type', 'application/dash+xml')
            cls = dash.Dash_transcoder
        elif settings.format == 'pipe':
            cls = pipe.Pipe_transcoder
        else:
            raise Exception('Unknown player')
        self.player: Transcoder = cls(settings=settings, metadata=metadata[0])
            
        ready = await self.player.start(self.write_data)
        if ready == False:
            self.set_status(500)
            self.write_object({"error": "Failed"})
            return

        if self.player.media_name:
            self.redirect(f'/files/{settings.session}/{self.player.media_name}')

    async def write_data(self, data):
        if data:
            self.write(data)
            await self.flush()

    def on_connection_close(self) -> None:
        if hasattr(self, 'player') and isinstance(self.player, pipe.Pipe_transcoder):
            self.player.close()

    def parse_settings(self) -> transcoders.base.Transcode_settings:
        try:
            args: Transcode_setting_arguments = utils.validate_schema(
                Transcode_setting_arguments, 
                escape.recursive_unicode(self.request.arguments)
            )
        except utils.Validation_exception as e:
            raise exceptions.Validation_exception(errors=e.errors)
        
        def comma_list(list):
            for a in list:
                for b in a.split(','):
                    yield b
        def element(ele):
            return ele[0] if ele and ele[0] else None
        if args.start_time and args.start_time[0]:
            args.start_time[0] = int(args.start_time[0])
        return transcoders.base.Transcode_settings(
            play_id=args.play_id[0],
            session=args.session[0],
            supported_pixel_formats=comma_list(args.supported_pixel_formats),
            format=args.format[0],
            transcode_codec=args.transcode_codec[0],
            transcode_pixel_format=args.transcode_pixel_format[0],
            start_time=element(args.start_time),
            audio_lang=element(args.audio_lang),
            subtitle_lang=element(args.subtitle_lang),
            audio_channels=element(args.audio_channels),
            width=element(args.width),
            audio_channels_fix=element(args.audio_channels_fix),
        )

class Source_handler(Base_handler):

    async def get(self):
        metadata = await get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No movie/episode found"}')
            return
        try:
            self.set_content_type(metadata[0]['format']['filename'])
            async with async_open(metadata[0]['format']['filename'], 'rb') as f:
                self.set_header('Content-Length', os.fstat(f.file.fileno()).st_size)
                async for chunk in f.iter_chunked(128*1024):
                    self.write(chunk)
                    try:
                        await self.flush()
                    except:
                        pass
        except FileNotFoundError:
            self.set_status(404)
            self.write_object({'error': 'Unknown segment'})

    def set_content_type(self, path):
        mime_type, encoding = mimetypes.guess_type(path)
        if encoding == "gzip":
            t = "application/gzip"
        elif encoding is not None:
            t = "application/octet-stream"
        elif mime_type is not None:
            t = mime_type
        else:
            t = "application/octet-stream"
        self.set_header('Content-Type', t)

class Close_session_handler(Base_handler):

    async def get(self, session: str):
        if session not in transcoders.base.sessions:
            self.set_status(404)
            self.write_object({'error': 'Unknown session'})
            return
        transcoders.base.close_session(session)

class Keep_alive_handler(Base_handler):

    def get(self, session: str):
        if session not in transcoders.base.sessions:
            self.set_status(404)
            self.write_object({'error': 'Unknown session'})
            return
        loop = asyncio.get_event_loop()
        transcoders.base.sessions[session].call_later.cancel()
        transcoders.base.sessions[session].call_later = loop.call_later(
            config.data.play.session_timeout,
            transcoders.base.close_session_callback,
            session
        )
        self.set_status(204)

class File_handler(Base_handler):
    
    async def get(self, path):
        try:
            path = os.path.join(config.data.play.temp_folder, path)
            async with async_open(path, 'rb') as f:
                self.set_header('Content-Length', os.fstat(f.file.fileno()).st_size)
                async for chunk in f.iter_chunked(128*1024):
                    self.write(chunk)
                    try:
                        await self.flush()
                    except:
                        pass
        except FileNotFoundError:
            self.set_status(404)
            self.write_object({'error': 'Unknown segment'})

    def should_return_304(self):
        return False

class Metadata_handler(web.RequestHandler):

    async def get(self):
        metadata = await get_metadata(self.get_argument('play_id'))
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No movie/episode found"}')
            return
        for m in metadata:
            m['format'].pop('filename')
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
        secret=config.data.play.secret,
        name='play_id',
        value=play_id,
        max_age_days=0.3,
    )
    if not data:
        raise web.HTTPError(400, 'Play id invalid')
    return utils.json_loads(data)

def tornado_auto_reload():
    logging.debug('Reloading and closing sessions')
    for session in list(transcoders.base.sessions):
        transcoders.base.close_session(session)
import tornado.autoreload
tornado.autoreload.add_reload_hook(tornado_auto_reload)