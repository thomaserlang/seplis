import asyncio, os
import logging
from typing import Dict
from seplis import config
from .video import stream_index_by_lang, to_subprocess_arguments

async def get_subtitle_file(metadata: Dict, lang: str, start_time: int):
    if not lang:
        return
    sub_index = stream_index_by_lang(metadata, 'subtitle', lang)
    if not sub_index:
        return
    args = [
        {'-ss': str(start_time)},
        {'-i': metadata['format']['filename']},
        {'-y': None},
        {'-vn': None},
        {'-an': None},
        {'-c:s': 'webvtt'},
        {'-map': f'0:s:{sub_index.group_index}'},
        {'-f': 'webvtt'},
        {'-': None},
    ]
    args = to_subprocess_arguments(args)        
    logging.debug(f'Subtitle args: {" ".join(args)}')
    process = await asyncio.create_subprocess_exec(
        os.path.join(config.data.play.ffmpeg_folder, 'ffmpeg'),
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logging.warning(f'Subtitle file could not be exported!: {stderr}')
        return None
    return stdout