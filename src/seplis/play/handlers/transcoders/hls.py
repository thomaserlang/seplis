import asyncio, os
from aiofile import async_open
from seplis import config
from . import base

class Hls_transcoder(base.Transcoder):
    
    def ffmpeg_extend_args(self) -> None:
        self.ffmpeg_args.extend([
            {'-f': 'hls'},
            {'-hls_playlist_type': 'event'},
            {'-hls_segment_type': config.data.play.ffmpeg_hls_segment_type},
            {'-hls_time': str(config.data.play.segment_time)},
            {'-hls_list_size': '0'},
            {self.media_path: None},
        ])

    @property
    def media_path(self) -> str:
        return os.path.join(self.temp_folder, self.media_name)

    @property
    def media_name(self) -> str:
        return 'media.m3u8'

    async def wait_for_media(self) -> bool:
        files = 0

        while True:
            await asyncio.sleep(0.5)
            if os.path.exists(self.media_path):
                async with async_open(self.media_path, "r") as afp:
                    async for line in afp:                        
                        if not '#' in line:
                            files += 1   
            if files >= 1:
                return True