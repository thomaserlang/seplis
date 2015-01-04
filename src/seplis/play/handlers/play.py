import logging
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.escape
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
        )
        self.fd = self.process.stdout.fileno()
        def receive_data(*args):
            data = self.process.stdout.read(8192)
            if self.process.stderr:
                error = self.process.stderr.read()
                if error:
                    logging.error(error)
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
            '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={}'.format(
                int(self.metadata['format']['bit_rate'])
            ),
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
        runtime = int(float(
            self.metadata['format']['duration']
        ))
        cmd.append('-segment_list')
        cmd.append(os.path.join(path, 'media.m3u8'))
        cmd.append(os.path.join(path, '%05d.ts'))
        process = subprocess.Popen(
            cmd
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

    @tornado.web.asynchronous
    def get(self):
        self.session = self.get_argument('session')
        self.ioloop = tornado.ioloop.IOLoop.current()
        device_name = self.get_device_name()
        device = config['play']['devices'][device_name]
        episode = get_episode(self.get_argument('play_id'))
        if not episode:
            raise tornado.web.HTTPError(404)
        file_path = episode.path
        self.metadata = episode.meta_data
        cmd = self.get_transcode_arguments(
            file_path,
            device_name,
        )
        self.set_start_time(cmd)
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
        l = len(cmd)
        cmd.insert(1, '-ss')
        cmd.insert(2, str(start))

    def on_connection_close(self):
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

    def get_codec_name(self, file_path):

        if 'streams' not in self.metadata:
            return
        for stream in self.metadata['streams']:
            if stream['codec_type'] == 'video':
                return stream['codec_name']

    def get_codec(self, file_path, device):
        codec = self.get_codec_name(file_path)
        if codec:
            logging.info('"{}" has codec type: "{}"'.format(file_path, codec))
        else:        
            logging.info('Could not find a codec for "{}"'.format(file_path))
        if codec in device['names']:
            return 'copy'
        return device['default_codec']

    def get_transcode_arguments(self, file_path, device_name):
        device_name = device_name if device_name in config['play']['devices'] else 'default'
        device = config['play']['devices'][device_name]
        vcodec = self.get_codec(
            file_path, 
            device
        )
        logging.info('"{}" will be transcoded with codec "{}", with settings from device "{}"'.format(
            file_path, 
            vcodec,
            device_name
        ))
        if device['type'] == 'stream':
            return self.get_transcode_arguments_stream(file_path, vcodec)
        elif device['type'] == 'hls':
            return self.get_transcode_arguments_hls(file_path, vcodec)

    def get_transcode_arguments_stream(self, file_path, vcodec):
        cmd = [ 
            os.path.join(config['play']['ffmpeg_folder'], 'ffmpeg'),
            '-i', file_path,
            '-f', 'matroska',
            '-loglevel', 'quiet',
            '-threads', '0',
            '-y',
            '-map_metadata', '-1', 
            '-vcodec', vcodec,
            '-map', '0:0',
            '-sn',
            '-acodec', 'aac',
            '-strict', '-2',
            '-cutoff', '15000',
            '-ac', '2', 
            '-map', '0:1',
            '-ab', '193k',
            '-',
        ]
        if vcodec == 'copy':
            cmd.insert(1, '-noaccurate_seek')
        return cmd

    def get_transcode_arguments_hls(self, file_path, vcodec):
        return [       
            os.path.join(config['play']['ffmpeg_folder'], 'ffmpeg'),
            '-i', file_path,
            '-threads', '0',
            '-y',
            '-segment_format', 'mpegts',
            '-f', 'segment',
            '-loglevel', 'quiet',
            '-map_metadata', '-1', 
            '-vcodec', vcodec,
            '-flags',
            '-global_header',
            '-segment_time', str(config['play']['segment_time']), 
            '-segment_start_number', '0',
            '-bsf', 'h264_mp4toannexb',
            '-map', '0:0',
            '-sn',
            '-acodec', 'libmp3lame',
            '-ac', '2',
            '-map', '0:1',
            '-aq', '0',
            '-hls_allow_cache', '0',
        ]    

class Hls_file_handler(Transcode_handler, _hls_handler):

    @tornado.web.asynchronous
    def get(self, session, file_):
        self.ioloop = tornado.ioloop.IOLoop.current()
        self._get(session, file_)

    def _get(self, session, file_, times=1):
        if session not in self.sessions:
            raise tornado.web.HTTPError(500, 'unknown session')
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
            if 'media.m3u8' == file_:
                logging.info(s)
        call_later = self.ioloop.call_later(
            config['play']['session_timeout'], 
            self.cancel_transcode, 
            self.sessions[session]
        )
        self.sessions[session]['call_later'] = call_later
        self.finish()

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
        if session in self.sessions:
            self.cancel_transcode(
                self.sessions[session]
            )

    def set_default_headers(self):
        set_default_headers(self)

class Metadata_handler(tornado.web.RequestHandler):

    def get(self):
        episode = get_episode(
            self.get_argument('play_id'),
        )
        if not episode or not episode.meta_data:
            self.set_status(404)
            self.write('{}')
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