import logging
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.escape
import tornado.process
import subprocess
import os, os.path
import shutil
import time
import mimetypes
from seplis import config, utils, Async_client
from seplis.play import models
from seplis.play.decorators import new_session
from sqlalchemy import desc

class Play_shows_handler(tornado.web.RequestHandler):

    def get(self):
        with new_session() as session:
            shows = session.query(
                models.Show_id_lookup
            ).order_by(
                desc(models.Show_id_lookup.updated),
            ).all()
            self.render(
                'play_shows.html',
                shows=shows,
                config=config,
                url_escape=tornado.escape.url_escape
            )

    def post(self):
        set_default_headers(self)
        with new_session() as session:
            with session.no_autoflush:
                show = session.query(
                    models.Show_id_lookup,
                ).filter(
                    models.Show_id_lookup.file_show_title == \
                        self.get_argument('file_show_title')
                ).first()
                if not show:
                    raise tornado.web.HTTPError(404, 'show not found')
                old_show_id = show.show_id
                show.show_id = self.get_argument('show_id')            
                show.show_title = self.get_argument('show_title')
                if old_show_id:
                    count = session.query(
                        models.Show_id_lookup,
                    ).filter(
                        models.Show_id_lookup.show_id == old_show_id
                    ).count()
                    if count < 2:
                        session.query(
                            models.Episode_number_lookup,
                        ).filter(
                            models.Episode_number_lookup.show_id == old_show_id,
                        ).update({
                            'show_id': show.show_id,
                        })
                        session.query(
                            models.Episode,
                        ).filter(
                            models.Episode.show_id == old_show_id,
                        ).update({
                            'show_id': show.show_id,
                        })
                session.commit()
                self.write('{}')

class API_show_suggest_handler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        client = Async_client(config['client']['api_url'], version='1')
        set_default_headers(self)
        q = self.get_argument('q')
        shows = yield client.get('/shows', {
            'q': q,
            'fields': 'title,poster_image'
        })
        self.write(utils.json_dumps(shows))

class _stream_handler(object):

    def send_stream(self, cmd):
        self.set_header('Content-Type', 'video/x-matroska')
        def send(data):
            if data:
                self.write(data)
                self.flush()
            else:
                self.finish()                
        def close_fds():
            os.dup2(os.open('/dev/null', os.O_RDONLY), 0)
            os.close(2)
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            preexec_fn=close_fds,
            env=self.subprocess_env(),
        )
        self.fd = self.process.stdout.fileno()
        def receive_data(*args):
            data = self.process.stdout.read(8192)
            if data: 
                send(data)
            elif self.process.poll() is not None:
                self.ioloop.remove_handler(self.fd)
                self.fd = None
                send(None)
        self.ioloop.add_handler(self.fd, receive_data, self.ioloop.READ)

class _hls_handler(object):

    sessions = {}

    def send_hls(self, cmd):
        self.set_header('Content-Type', 'application/x-mpegURL')
        if self.session not in self.sessions:
            self.start_transcode(
                session=self.session,
                cmd=cmd,
            )
        else:
            self.ioloop.remove_timeout(
                self.sessions[self.session]['call_later']
            )
        a = [
            '#EXTM3U',
            '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1',
            '{}/media/media.m3u8'.format(self.session),
        ]
        for s in a:
            self.write(s+'\n')
        call_later = self.ioloop.call_later(
            config['play']['session_timeout'], 
            self.cancel_transcode, 
            self.sessions[self.session]
        )
        self.sessions[self.session]['call_later'] = call_later
        self.finish()

    def start_transcode(self, session, cmd):
        path = os.path.join(config['play']['temp_folder'], session)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        cmd.append('-hls_segment_filename')
        cmd.append(os.path.join(path, '%05d.ts'))
        cmd.append(os.path.join(path, 'media.m3u8'))
        process = subprocess.Popen(
            cmd,
            env=self.subprocess_env(),
        )
        self.sessions[session] = {
            'process': process,
            'path': os.path.join(path, 'media.m3u8'),
            'session': session,
        }            

    def cancel_transcode(self, session):
        logging.info('Closing session: {}'.format(session['session']))
        process = session['process']
        if process.returncode is None:
            process.terminate()
            process.wait()
        path = os.path.dirname(session['path'])
        if os.path.exists(path):
            shutil.rmtree(path)
        else:
            logging.warning('Path: {} not found, can\'t delete it'.format(session['path']))            
        tornado.ioloop.IOLoop.current().remove_timeout(session['call_later'])
        del self.sessions[session['session']]

class Transcode_handler(
    tornado.web.RequestHandler, 
    _hls_handler, 
    _stream_handler):

    def get_device_name(self):
        device_name = self.get_argument('device', 'default')
        device_name = device_name if device_name in config['play']['devices'] \
            else 'default'
        return device_name

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')

    def subprocess_env(self):
        env = {}
        if config['play']['ffmpeg_logfile']:
            env['FFREPORT'] = 'file=\'{}\':level={}'.format(
                config['play']['ffmpeg_logfile'],
                config['play']['ffmpeg_loglevel'],
            )
        return env

    def create_temp_folder(self):
        path = config['play']['temp_folder']
        if not os.path.exists(path):
            os.makedirs(path)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.create_temp_folder()
        self.session = self.get_argument('session')
        self.ioloop = tornado.ioloop.IOLoop.current()
        device_name = self.get_device_name()
        device = config['play']['devices'][device_name]
        episode = get_episode(self.get_argument('play_id'))
        if not episode:
            raise tornado.web.HTTPError(404)
        self.file_path = episode.path
        self.metadata = episode.meta_data
        self.video_stream = self.get_video_stream(self.metadata)
        if not self.video_stream:
            raise Exception('No video stream were found')
        self.audio_lang = self.get_argument('audio_lang', None)
        subtitle_lang = self.get_argument('subtitle_lang', None)
        self.subtitle_file = None
        if subtitle_lang:
            self.subtitle_file = yield self.subtitle(subtitle_lang)
        cmd = self.get_transcode_arguments(
            device_name,
        )
        self.type = device['type']
        if device['type'] == 'stream':
            self.send_stream(cmd)
        elif device['type'] == 'hls':            
            self.send_hls(cmd)

    def set_start_time(self, cmd):
        start = int(self.get_argument('start', 0))
        self.start_time = start
        if start == 0:
            return
        cmd.insert(1, '-ss')
        cmd.insert(2, str(start))

    def set_subtitle(self, cmd):
        if not self.subtitle_file:
            return        
        i = cmd.index('-i') + 1
        cmd.insert(i+1, '-vf')
        cmd.insert(i+2, 'subtitles={}'.format(self.subtitle_file))

    def set_audio(self, cmd):
        if not self.audio_lang:
            return
        d = self._get_stream_index_by_lang('audio', self.audio_lang)
        if not d: 
            return
        i = cmd.index('0:1')
        cmd[i] = '0:{}'.format(d['index'])

    def on_connection_close(self):
        if self.subtitle_file and os.path.exists(self.subtitle_file):
            os.remove(self.subtitle_file)
        if not hasattr(self, 'type'):
            return
        if self.type != 'stream':
            return
        if not self.process:
            return
        if self.process.returncode is not None:
            return
        self.process.stdout.close()
        self.process.terminate()
        self.process.wait()
        if self.fd:
            self.ioloop.remove_handler(self.fd)

    def get_video_stream(self, metadata):
        if 'streams' not in self.metadata:
            return
        for stream in self.metadata['streams']:
            if stream['codec_type'] == 'video':
                return stream

    def get_codec(self, device):
        codec = self.video_stream['codec_name']
        pix_fmt = self.video_stream['pix_fmt']
        if codec:
            logging.info('"{}" has codec type: "{}"'.format(self.file_path, codec))
        else:        
            logging.info('Could not find a codec for "{}"'.format(self.file_path))
        if not self.subtitle_file:
            if codec in device['names'] and pix_fmt in device['pix_fmt']:
                return 'copy'
        return device['default_codec']

    def get_transcode_arguments(self, device_name):
        device = config['play']['devices'][device_name]
        vcodec = self.get_codec(device)
        logging.info('"{}" will be transcoded with codec "{}", with settings from device "{}"'.format(
            self.file_path, 
            vcodec,
            device_name
        ))
        cmd = []
        if device['type'] == 'stream':
            cmd = self.get_transcode_arguments_stream(vcodec)
        elif device['type'] == 'hls':
            cmd = self.get_transcode_arguments_hls(vcodec)
        self.set_start_time(cmd)
        self.set_subtitle(cmd)
        self.set_audio(cmd)
        logging.debug(' '.join(cmd))
        return cmd

    def get_transcode_arguments_stream(self, vcodec):
        cmd = [ 
            os.path.join(config['play']['ffmpeg_folder'], 'ffmpeg'),
            '-i', self.file_path,
            '-f', 'matroska',
            '-loglevel', 'quiet',
            '-threads', str(config['play']['ffmpeg_threads']),
            '-y',
            '-map', '0:v:0',
            '-preset', 'veryfast',
            '-c:v', vcodec,
            '-pix_fmt', 'yuv420p',
            '-map', '0:a:0',
            '-c:a', 'aac',
            '-strict', '-2',
            '-cutoff', '15000',
            '-ac', '2', 
            '-ab', '193k',
            '-',
        ]
        if vcodec == 'copy':
            cmd.insert(1, '-noaccurate_seek')
        return cmd

    def get_transcode_arguments_hls(self, vcodec):
        return [       
            os.path.join(config['play']['ffmpeg_folder'], 'ffmpeg'),
            '-i', self.file_path,
            '-threads', str(config['play']['ffmpeg_threads']),
            '-y',
            '-preset', 'veryfast',
            '-loglevel', 'quiet',
            '-vcodec', vcodec,
            '-pix_fmt', 'yuv420p',
            '-bsf', 'h264_mp4toannexb',
            '-map', '0:v:0',
            '-acodec', 'libmp3lame',
            '-ac', '2',
            '-map', '0:a:0',
            '-hls_allow_cache', '0',
            '-hls_time', str(config['play']['segment_time']),
            '-hls_list_size', '0', 
        ]

    def _get_stream_index_by_lang(self, codec_type, lang):
        logging.info('Looking for {} with language {}'.format(codec_type, lang))
        group_index = -1
        langs = []
        index = None
        if ':' in lang:
            lang, index = lang.split(':')
            index = int(index)
            if index <= (len(self.metadata['streams']) - 1):
                stream = self.metadata['streams'][index]
                if not ('tags' in stream and 'language' in stream['tags'] and \
                    stream['codec_type'] == codec_type and \
                        stream['tags']['language'] == lang):
                    index = None
            else:
                index = None
        for i, stream in enumerate(self.metadata['streams']):
            if stream['codec_type'] == codec_type:
                group_index += 1
                if 'tags' in stream and 'language' in stream['tags']:
                    langs.append(stream['tags']['language'])
                    if not index or stream['index'] == index:
                        if stream['tags']['language'] == lang:
                            return {
                                'index': i,
                                'group_index': group_index,
                            }
        logging.info('Found no {} with language: {}'.format(codec_type, lang))
        logging.info('Available {}: {}'.format(codec_type, ', '.join(langs)))

    def get_subtitles_arguments(self, lang):
        sub_index = self._get_stream_index_by_lang('subtitle', lang)
        if not sub_index:
            return
        args = [
            os.path.join(config['play']['ffmpeg_folder'], 'ffmpeg'),
            '-i', self.file_path,
            '-y',
            '-vn',
            '-an',
            '-c:s:{}'.format(sub_index['group_index']),
            'ass',
        ]
        start = int(self.get_argument('start', 0))
        if start:
            args.insert(1, '-ss')
            args.insert(2, str(start))
        return args

    @tornado.gen.coroutine
    def subtitle(self, lang):
        args = self.get_subtitles_arguments(lang)
        if not args:
            return 
        subtitle_file = os.path.join(
            config['play']['temp_folder'],
            '{}.ass'.format(self.session)
        )
        logging.info('Subtitle found, saving to: {}'.format(subtitle_file))
        args.append(subtitle_file)
        logging.info('Subtitle arguments: {}'.format(' '.join(args)))
        p = tornado.process.Subprocess(
            args,
            env=self.subprocess_env(),
        )
        r = yield p.wait_for_exit(raise_error=True)
        if r != 0:
            logging.info('Subtitle file could not be saved!')
            return
        logging.info('Subtitle file saved!')
        return subtitle_file

class Hls_file_handler(Transcode_handler, _hls_handler):

    @tornado.web.asynchronous
    def get(self, session, file_):
        self.ioloop = tornado.ioloop.IOLoop.current()
        self._get(session, file_)

    def _get(self, session, file_, times=1):
        if session not in self.sessions:
            raise tornado.web.HTTPError(404, 'unknown session')
        self.ioloop.remove_timeout(self.sessions[session]['call_later'])
        path = os.path.join(config['play']['temp_folder'], session, file_)  
        # if the file type is m3u8 and it is not found, we'll try again.
        if 'media.m3u8' == file_:
            if times > 20:
                raise tornado.web.HTTPError(404)
            if not os.path.exists(path) or (os.stat(path).st_size == 0):
                logging.info('media.m3u8 not found, trying again in 1 second. Retry number: {}'.format(times))
                times += 1
                self.ioloop.call_later(
                    1, 
                    self._get, 
                    session, 
                    file_, 
                    times
                )
                return        
        with open(path, 'rb') as f:
            s = f.read()
            self.write(s)
        call_later = self.ioloop.call_later(
            config['play']['session_timeout'], 
            self.cancel_transcode, 
            self.sessions[session]
        )
        self.sessions[session]['call_later'] = call_later
        self.finish()

    def on_connection_close(self):
        pass

def set_default_headers(self):
    self.set_header('Cache-Control', 'no-cache, must-revalidate')
    self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    self.set_header('Content-Type', 'application/json')
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since, X-Requested-With')
    self.set_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE')
    self.set_header('Access-Control-Expose-Headers', 'ETag, Link, X-Total-Count, X-Total-Pages')
    self.set_header('Access-Control-Max-Age', '86400')
    self.set_header('Access-Control-Allow-Credentials', 'true')

class Hls_cancel_handler(Transcode_handler, _hls_handler):

    def get(self, session):
        if session not in self.sessions:
            raise tornado.web.HTTPError(404, 'unknown session')

        self.cancel_transcode(
            self.sessions[session]
        )

    def set_default_headers(self):
        set_default_headers(self)


class Hls_ping_handler(tornado.web.RequestHandler, _hls_handler):

    def get(self, session):
        self.ioloop = tornado.ioloop.IOLoop.current()
        if session not in self.sessions:
            raise tornado.web.HTTPError(404, 'unknown session')
        self.ioloop.remove_timeout(self.sessions[session]['call_later'])
        call_later = self.ioloop.call_later(
            config['play']['session_timeout'], 
            self.cancel_transcode, 
            self.sessions[session]
        )
        self.sessions[session]['call_later'] = call_later


    def set_default_headers(self):
        set_default_headers(self)

class Metadata_handler(tornado.web.RequestHandler):

    def get(self):
        episode = get_episode(
            self.get_argument('play_id'),
        )
        if not episode:
            self.set_status(404)
            self.write('{"error": "No episode found"}')
            return
        if not episode.meta_data:
            self.set_status(404)
            self.write('{"error": "No metadata for the episode found"}')
            return
        self.write(
            episode.meta_data,
        )

    def set_default_headers(self):
        set_default_headers(self)

class Play_handler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        episode = get_episode(self.get_argument('play_id'))
        content_type = mimetypes.guess_type(episode.path)
        if content_type:            
            self.add_header('Content-Type', content_type[0])
        if config['play']['x-accel']:
            self.add_header('X-Accel-Redirect', '/source'+episode.path)
            self.finish()
        else:
            if not episode:
                raise tornado.web.HTTPError(404)
            with open(episode.path, 'rb') as f:
                while 1:
                    data = f.read(16384)
                    if not data: 
                        break
                    self.write(data)
            self.finish()

def decode_play_id(play_id):
    return utils.json_loads(tornado.web.decode_signed_value(
        secret=config['play']['secret'],
        name='play_id',
        value=play_id,
        max_age_days=1,
    ))

def get_episode(play_id):
    play_info = decode_play_id(
        play_id,
    )
    with new_session() as session:
        episode = session.query(
            models.Episode.path,
            models.Episode.meta_data,
        ).filter(
            models.Episode.show_id == play_info['show_id'],
            models.Episode.number == play_info['number'],
        ).first()
        return episode