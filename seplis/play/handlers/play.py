import asyncio, os, http
from typing import List, Optional, Union
from aiofile import async_open
from pydantic import BaseModel, conlist, constr
from sqlalchemy import select
from tornado import web, escape
from seplis.api import exceptions
from seplis.play.connections import database
from seplis.play.handlers.transcoders import dash, pipe
from seplis.play.handlers.transcoders.subtitle import get_subtitle_file
from seplis.play.handlers.transcoders.video import Transcoder, get_video_stream
from .transcoders import hls
from seplis import config, utils, logger
from seplis.play import models
from seplis.play.handlers import transcoders


class Source_arguments(BaseModel):
    play_id: conlist(str, min_items=1, max_items=1)
    source_index: conlist(int, max_items=1) = [0]    

class Transcode_setting_arguments(Source_arguments):
    session: conlist(str, min_items=1, max_items=1)
    supported_video_codecs: List[str] = ['h264']
    supported_audio_codecs: List[str] = ['acc']
    supported_pixel_formats: List[str] = ['yuv420p']
    format: conlist(str, min_items=1, max_items=1) = ['hls']
    transcode_video_codec: conlist(str, max_items=1) = ['h264']
    transcode_audio_codec: conlist(str, max_items=1) = ['aac']
    transcode_pixel_format: conlist(str, max_items=1) = ['yuv420p']

    start_time: conlist(Union[int, float], max_items=1) = [0]
    audio_lang: Optional[conlist(Optional[str], max_items=1)]
    audio_channels: Optional[conlist(Optional[int], max_items=1)]
    width: Optional[conlist(Union[int, constr(max_length=0), None], max_items=1)]
    client_width: Optional[conlist(Union[int, constr(max_length=0), None], max_items=1)]

class Subtitle_arguments(Source_arguments):

    lang: conlist(constr(min_length=1), min_items=1, max_items=1)
    start_time: conlist(Union[int, float], max_items=1) = [0]

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

    def validate_arguments(self, schema):
        try:
            return utils.validate_schema(
                schema, 
                escape.recursive_unicode(self.request.arguments)
            )
        except utils.Validation_exception as e:
            raise exceptions.Validation_exception(errors=e.errors)

class Transcode_handler(Base_handler):

    async def get(self):
        args: Transcode_setting_arguments = self.validate_arguments(Transcode_setting_arguments)
        settings = self.parse_settings(args)
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
        self.player: Transcoder = cls(settings=settings, metadata=metadata[args.source_index[0]])
            
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

    def parse_settings(self, args: Transcode_setting_arguments) -> transcoders.video.Transcode_settings:        
        def comma_list(list):
            for a in list:
                for b in a.split(','):
                    yield b
                    
        def element(ele):
            return ele[0] if ele and ele[0] else None

        if args.start_time and args.start_time[0]:
            args.start_time[0] = int(args.start_time[0])

        return transcoders.video.Transcode_settings(
            play_id=args.play_id[0],
            session=args.session[0],
            supported_video_codecs=comma_list(args.supported_video_codecs),
            supported_audio_codecs=comma_list(args.supported_audio_codecs),
            supported_pixel_formats=comma_list(args.supported_pixel_formats),
            format=args.format[0],
            transcode_video_codec=args.transcode_video_codec[0],
            transcode_audio_codec=args.transcode_audio_codec[0],
            transcode_pixel_format=args.transcode_pixel_format[0],
            start_time=element(args.start_time),
            audio_lang=element(args.audio_lang),
            audio_channels=element(args.audio_channels),
            width=element(args.width),
            client_width=element(args.client_width),
        )

class Sources_handler(Base_handler):

    async def get(self):
        args: Source_arguments = self.validate_arguments(Source_arguments)
        sources = await get_metadata(args.play_id[0])
        if not sources:
            self.set_status(404)
            self.write('{"error": "No movie/episode found"}')
            return
        data = []
        for i, source in enumerate(sources):
            video = get_video_stream(source)
            d = {
                'width': video['width'],
                'height': video['height'],
                'codec': video['codec_name'],
                'duration': float(source['format']['duration']),
                'audio': [],
                'subtitles': [],
                'index': i
            }
            data.append(d)
            for stream in source['streams']:
                if 'tags' not in stream:
                    continue
                title = stream['tags'].get('title')
                lang = stream['tags'].get('language')
                if not title and not lang:
                    continue
                s = {
                    'title': title or lang,
                    'language': lang or title,
                    'index': stream['index'],
                    'codec': stream.get('codec_name'),
                }
                if stream['codec_type'] == 'audio':
                    d['audio'].append(s)
                elif stream['codec_type'] == 'subtitle':
                    if stream['codec_name'] not in ('dvd_subtitle', 'hdmv_pgs_subtitle'):
                        d['subtitles'].append(s)
        self.write_object(sorted(data, key=lambda x: x['width']))

class Subtitle_file_handler(Base_handler):

    async def get(self):
        args: Subtitle_arguments = self.validate_arguments(Subtitle_arguments)
        metadata = await get_metadata(args.play_id[0])
        if not metadata:
            self.set_status(404)
            self.write('{"error": "No movie/episode found"}')
            return
        sub = await get_subtitle_file(metadata=metadata[args.source_index[0]], lang=args.lang[0], start_time=int(args.start_time[0]))
        if not sub:
            self.set_status(500)
            self.write_object({'error': 'Unable retrive subtitle file'})
            return
        self.set_header('Content-Type', 'text/vtt')
        self.write(sub)

class Close_session_handler(Base_handler):

    async def get(self, session: str):
        if session not in transcoders.video.sessions:
            self.set_status(404)
            self.write_object({'error': 'Unknown session'})
            return
        transcoders.video.close_session(session)

class Keep_alive_handler(Base_handler):

    def get(self, session: str):
        if session not in transcoders.video.sessions:
            self.set_status(404)
            self.write_object({'error': 'Unknown session'})
            return
        loop = asyncio.get_event_loop()
        transcoders.video.sessions[session].call_later.cancel()
        transcoders.video.sessions[session].call_later = loop.call_later(
            config.data.play.session_timeout,
            transcoders.video.close_session_callback,
            session
        )
        self.set_status(204)

class File_handler(Base_handler):
    
    async def get(self, path):        
        path = os.path.join(config.data.play.temp_folder, path)
        if os.path.commonprefix((os.path.realpath(path), config.data.play.temp_folder)) != str(config.data.play.temp_folder):
            self.set_status(404)
            self.write_object({'error': 'File not found'})
            return
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
            self.write_object({'error': 'File not found'})

    def should_return_304(self):
        return False

class Thumbnails_handler(web.StaticFileHandler):

    def initialize(self) -> None:
        return super().initialize(config.data.play.thumbnails_path)
    
    async def get(self, path: str, include_body: bool = True) -> None:
        data = decode_play_id(self.get_argument('play_id'))
        if data['type'] == 'series':
            path = f"episode-{data['series_id']}-{data['number']}/{path}"
        elif data['type'] == 'movie':
            path = f"movie-{data['movie_id']}/{path}"
        return await super().get(path, include_body)

    def options(self, *args, **kwargs):
        self.set_status(204)

    def set_default_headers(self) -> None:
        self.set_header('Content-Type', 'image/webp')
        self.set_header('Cache-Control', 'max-age=604800')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'User-Agent, Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Expose-Headers', 'Content-Type')

async def get_metadata(play_id):
    data = decode_play_id(play_id)
    async with database.session_async() as session:
        if data['type'] == 'series':
            query = select(models.Episode.meta_data).where(
                models.Episode.series_id == data['series_id'],
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
    logger.debug('Reloading and closing sessions')
    for session in list(transcoders.video.sessions):
        transcoders.video.close_session(session)
import tornado.autoreload
tornado.autoreload.add_reload_hook(tornado_auto_reload)