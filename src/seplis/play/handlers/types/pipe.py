import os
import subprocess
import logging
from types import MethodType

from . import base

__all__ = ['start']

def start(handler, settings, metadata):
    logging.debug('Pipe')
    action = handler.get_argument('action', None)
    if action:
        logging.debug('Action: {}'.format(action))
        handler.set_status(204)
        handler.finish()
        return
    def receive_data(*args):
        data = handler.process.stdout.read(8192)
        if data: 
            send_data(data)
        elif handler.process.poll() is not None:
            handler.ioloop.remove_handler(handler.fd)
            handler.fd = None
            send_data(None)
    def send_data(data):
        if data:
            handler.write(data)
            handler.flush()
        else:
            handler.finish()
    def close_fds():
        os.dup2(os.open('/dev/null', os.O_RDONLY), 0)
        os.close(2) 
    handler.event_connection_close = MethodType(connection_close, handler)
    handler.set_header('Content-Type', 'video/x-matroska')
    handler.process = subprocess.Popen(
        ffmpeg_start(handler, settings, metadata),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,            
        close_fds=True,
        preexec_fn=close_fds,
        env=base.subprocess_env(),
    )
    handler.fd = handler.process.stdout.fileno()
    logging.debug('Process started. Fileno: {}'.format(handler.fd))
    handler.ioloop.add_handler(handler.fd, receive_data, handler.ioloop.READ)

def connection_close(self):
    logging.debug('Connection close requested')
    if not hasattr(self, 'process'):
        logging.debug('No process attr')
        return
    if self.process.returncode is not None:
        logging.debug('No process returncode')
        return
    logging.debug('Closing the FFmpeg process')
    self.process.stdout.close()
    self.process.terminate()
    self.process.wait()
    if self.fd:
        self.ioloop.remove_handler(self.fd)

def ffmpeg_start(handler, settings, metadata):
    args = base.ffmpeg_base_args(handler, settings, metadata)
    args.extend([
        {'-f': 'matroska'},
        {'-': None},
    ])
    if base.find_ffmpeg_arg('-c:v', args) == 'copy':
        args.insert(1, {'-noaccurate_seek': None})
    logging.debug('FFmpeg start args: {}'.format(args))
    return base.to_subprocess_arguments(args)