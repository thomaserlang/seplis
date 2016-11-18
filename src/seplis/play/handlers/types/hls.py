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
    media_file = 'media.m3u8'
    if handler.agent['os']['family'] == 'iOS':
        media_file = 'media2.m3u8'
    if session in sessions:        
        wait_for_media(handler, metadata, path, media_file, session)
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
    if media_file == 'media2.m3u8':
        generate_media(handler, metadata, path)
    wait_for_media(handler, metadata, path, media_file, session)

def wait_for_media(handler, metadata, path, media_file, session, times=0):
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
            media_file,
            session,
            times,
        )
        return
    media = [
        '#EXTM3U',
        '#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1',
        '/hls/{}/{}'.format(session, media_file),
    ]
    for s in media:
        handler.write(s+'\n')
    handler.finish()
    
def generate_media(handler, metadata, path):
    with open(os.path.dirname(path)+'/media2.m3u8', 'w') as f:
        start_time = int(handler.get_argument('start_time', 0))
        duration = float(metadata['format']['duration']) - start_time
        f.write('#EXTM3U\n')
        f.write('#EXT-X-VERSION:3\n')
        f.write('#EXT-X-TARGETDURATION:3\n')
        f.write('#EXT-X-MEDIA-SEQUENCE:0\n')
        for i in range(0, int(duration/config['play']['segment_time'])):
            f.write('#EXTINF:3,\n')
            f.write('{}'.format(i).zfill(5)+'.ts\n')
        rest = duration % config['play']['segment_time']
        if rest > 0:
            f.write('#EXTINF:{},\n'.format(int(rest)))
            f.write('{}'.format(i+1).zfill(5)+'.ts\n')
        f.write('#EXT-X-ENDLIST')

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
    session = handler.get_argument('session')
    args = base.ffmpeg_base_args(handler, settings, metadata)
    if handler.agent['os']['family'] == 'iOS':
        base.change_ffmpeg_arg('-c:v', args, settings['transcode_codec'])
    args.extend([
        {'-f': 'hls'},
        {'-hls_flags': 'round_durations'},
        {'-hls_list_size': '0'},
        {'-hls_time': str(config['play']['segment_time'])},
        {'-force_key_frames': 'expr:gte(t,n_forced*{})'.format(config['play']['segment_time'])},
        {'-hls_segment_filename': os.path.join(temp_folder, '%05d.ts')},
        {os.path.join(temp_folder, 'media.m3u8'): None},
    ])
    return base.to_subprocess_arguments(args)

def setup_temp_folder(session):
    temp_folder = os.path.join(config['play']['temp_folder'], session)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    return temp_folder