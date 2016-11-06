import os
import subprocess
import logging
from types import MethodType

from . import base

__all__ = ['start']

def start(handler, settings, metadata):
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
    handler.ioloop.add_handler(handler.fd, receive_data, handler.ioloop.READ)

def connection_close(self):
    if self.process.returncode is not None:
        return
    self.process.stdout.close()
    self.process.terminate()
    self.process.wait()
    if self.fd:
        self.ioloop.remove_handler(self.fd)

def ffmpeg_start(handler, settings, metadata):
    args = base.ffmpeg_base_args(handler, settings, metadata)
    args.extend([
        {'-f': 'matroska'},
        {'-c:a': 'aac'},
        {'-strict': '-2'},
        {'-cutoff': '15000'},
        {'-ac': '2'},
        {'-ab': '193k'},
        {'-': None},
    ])
    if base.find_ffmpeg_arg('-c:v', args) == 'copy':
        args.insert(1, {'-noaccurate_seek': None})
    return base.to_subprocess_arguments(args)