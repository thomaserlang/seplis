import subprocess
import logging
import os, shutil
import tornado.ioloop

from seplis import config
from . import base

__all__ = ['start']

sessions = {}

def start(handler, settings, metadata):
    handler.set_header('Content-Type', 'application/x-mpegURL')
    session = handler.get_argument('session')
    action = handler.get_argument('action', None)
    if action == 'ping':
        ping(handler, session)
        handler.finish()
        return
    elif action == 'close':
        close(session)
        handler.finish()
        return
    temp_folder = setup_temp_folder(session)
    path = os.path.join(temp_folder, 'media.m3u8')
    if session in sessions:        
        wait_for_media(handler, metadata, path, session)
        return
    process = subprocess.Popen(
        ffmpeg_start(temp_folder, handler, settings, metadata),
        env=base.subprocess_env(),
    )
    call_later = handler.ioloop.call_later(
        config['play']['session_timeout'],
        cleanup,
        session,
    )
    sessions[session] = {
        'process': process,
        'temp_folder': temp_folder,
        'call_later': call_later,
    }
    wait_for_media(handler, metadata, path, session)


def wait_for_media(handler, metadata, path, session, times=0):
    times = 0
    ts_files = 0
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                if '.ts' in line:
                    ts_files += 1    
    if not os.path.exists(path) or (ts_files < 4):
        times += 1
        handler.ioloop.call_later(
            0.05,
            wait_for_media,
            handler,
            metadata,
            path,
            session,
            times,
        )
        return
    media = [
        '#EXTM3U',
        '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1',
        '/hls/{}/media.m3u8'.format(session),
    ]
    for s in media:
        handler.write(s+'\n')
    handler.finish()

def ping(handler, session):
    if session not in sessions:
        return
    handler.ioloop.remove_timeout(sessions[session]['call_later'])
    sessions[session]['call_later'] = handler.ioloop.call_later(
        config['play']['session_timeout'],
        cleanup,
        session,
    )

def cleanup(session):
    logging.info('Closing session: {}'.format(session))
    if session not in sessions:
        return
    s = sessions[session]
    logging.info(s['process'].returncode)
    if s['process'].returncode is None:
        s['process'].terminate()
        s['process'].wait()
    path = os.path.dirname(s['temp_folder'])
    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        logging.warning('Path: {} not found, can\'t delete it'.format(s['temp_folder']))            
    tornado.ioloop.IOLoop.current().remove_timeout(s['call_later'])
    del sessions[session]

def ffmpeg_start(temp_folder, handler, settings, metadata):
    args = base.ffmpeg_base_args(handler, settings, metadata)
    args.extend([
        {'-f': 'hls'},
        {'-c:a': 'libfaac'},
        {'-strict': '-2'},
        {'-cutoff': '15000'},
        {'-ac': '2'},
        {'-hls_flags': 'omit_endlist'},
        {'-hls_allow_cache': '0'},
        {'-hls_list_size': '0'},
        {'-hls_time': str(config['play']['segment_time'])},
        {'-hls_segment_filename': os.path.join(temp_folder, '%05d.ts')},
        {os.path.join(temp_folder, 'media.m3u8'): None},
    ])
    return base.to_subprocess_arguments(args)

def setup_temp_folder(session):
    temp_folder = os.path.join(config['play']['temp_folder'], session)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    return temp_folder