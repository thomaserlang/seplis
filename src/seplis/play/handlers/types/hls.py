from curses import meta
import subprocess
import logging
import os, shutil
import tornado.ioloop

from seplis import config
from . import base

__all__ = ['start']

sessions = {}

def start(handler, settings, metadata):
    logging.debug('HLS')
    handler.set_header('Content-Type', 'application/x-mpegurl')
    session = handler.get_argument('session')
    action = handler.get_argument('action', None)
    if action:        
        logging.debug('Action: {}'.format(action))
    if action == 'ping':
        ping(handler, session)
        handler.set_status(204)
        handler.finish()
        return
    elif action == 'cancel':
        cancel(session)
        handler.set_status(204)
        handler.finish()
        return
    temp_folder = setup_temp_folder(session)
    media_file = 'media.m3u8'
    path = os.path.join(temp_folder, media_file)
    if session in sessions:        
        wait_for_media(handler, metadata, path, media_file, session)
        return
    logging.debug('Creating new HLS file: {}'.format(path))
    process = subprocess.Popen(
        ffmpeg_start(temp_folder, handler, settings, metadata),
        env=base.subprocess_env(),
        cwd=temp_folder,
    )
    call_later = handler.ioloop.call_later(
        config['play']['session_timeout'],
        cancel,
        session,
    )
    sessions[session] = {
        'process': process,
        'temp_folder': temp_folder,
        'call_later': call_later,
    }
    wait_for_media(handler, metadata, path, media_file, session)

def wait_for_media(handler, metadata, path, media_file, session, times=0):
    ts_files = 0
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                if not '#' in line:
                    ts_files += 1    
    if not os.path.exists(path) or (ts_files < 1):
        times += 1
        handler.ioloop.call_later(
            0.05,
            wait_for_media,
            handler,
            metadata,
            path,
            media_file,
            session,
            times,
        )
        return
    handler.redirect(f'/hls/{session}/{media_file}')

def ping(handler, session):
    if session not in sessions:
        return
    handler.ioloop.remove_timeout(sessions[session]['call_later'])
    sessions[session]['call_later'] = handler.ioloop.call_later(
        config['play']['session_timeout'],
        cancel,
        session,
    )

def cancel(session):
    logging.info('Closing session: {}'.format(session))
    if session not in sessions:
        return
    s = sessions[session]
    if s['process'].returncode is None:
        s['process'].terminate()
        s['process'].wait()
    path = s['temp_folder']
    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        logging.warning('Path: {} not found, can\'t delete it'.format(path))            
    tornado.ioloop.IOLoop.current().remove_timeout(s['call_later'])
    del sessions[session]

def ffmpeg_start(temp_folder, handler, settings, metadata):
    args = base.ffmpeg_base_args(handler, settings, metadata)
    if handler.agent['os']['family'] == 'iOS':
        base.change_ffmpeg_arg('-c:v', args, settings['transcode_codec'])

    # Fix for hls.js eac3 or ac3 not playing
    if settings.get('audio_channels_fix'):
        a = base.stream_index_by_lang(metadata, 'audio', handler.get_argument('audio_lang', None))
        if a and metadata['streams'][a['index']]['codec_name'] in ('eac3', 'ac3',):
            args.append({'-ac': str(metadata['streams'][a['index']]['channels'])})            
            
    args.extend([
        {'-f': 'hls'},
        {'-hls_playlist_type': 'event'},
        {'-hls_segment_type': config['play']['ffmpeg_hls_segment_type']},
        {'-hls_time': str(config['play']['segment_time'])},
        {os.path.join(temp_folder, 'media.m3u8'): None},
    ])
    r = base.to_subprocess_arguments(args)
    logging.debug('FFmpeg start args: {}'.format(' '.join(r)))
    return r

def setup_temp_folder(session):
    temp_folder = os.path.join(config['play']['temp_folder'], session)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    return temp_folder

def tornado_auto_reload():
    for session in list(sessions):
        cancel(session)
import tornado.autoreload
tornado.autoreload.add_reload_hook(tornado_auto_reload)