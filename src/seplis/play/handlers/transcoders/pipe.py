import asyncio
import os
import subprocess
import logging
from typing import Union

from seplis import config

from . import base

class Pipe_transcoder(base.Transcoder):
    
    def ffmpeg_extend_args(self) -> None:
        self.ffmpeg_args.extend([
            {'-f': 'matroska'},
            {'-': None},
        ])

        if self.find_ffmpeg_arg('-c:v') == 'copy':
            self.ffmpeg_args.insert(1, {'-noaccurate_seek': None})

    @property
    def media_path(self) -> str:
        return None

    @property
    def media_name(self) -> str:
        return None

    async def wait_for_media(self) -> bool:
        return None

    async def start(self, send_data_callback) -> Union[bool, bytes]:     
        self.set_ffmpeg_args()        
        args = self.to_subprocess_arguments()   
        logging.debug(f'FFmpeg start args: {" ".join(args)}')
        self.process = await asyncio.create_subprocess_exec(
            os.path.join(config.data.play.ffmpeg_folder, 'ffmpeg'),
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.subprocess_env(),
        )
        self.register_session()
        while True:
            data = await asyncio.wait_for(self.process.stdout.read(8192), 10)
            if not data:
                return
            try:
                await send_data_callback(data)
            except:
                self.process.terminate()
                return

    def close(self) -> None:
        try:
            self.process.kill()
        except:
            pass