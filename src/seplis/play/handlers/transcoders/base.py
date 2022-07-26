import os, asyncio
import logging
import shutil
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel
from seplis import config

class Transcode_settings(BaseModel):

    play_id: str
    session: str
    supported_pixel_formats: List[str]
    format: Literal['pipe', 'hls', 'dash']
    transcode_codec: Literal['h264', 'hevc', 'vp9']
    transcode_pixel_format: Literal['yuv420p', 'yuv420p10le']

    start_time: Optional[int]
    audio_lang: Optional[str]
    subtitle_lang: Optional[str]
    audio_channels: Optional[int]
    width: Optional[int]
    audio_channels_fix: bool = True

class Session_model(BaseModel):
    process: asyncio.subprocess.Process
    temp_folder: Optional[str]
    call_later: asyncio.TimerHandle

    class Config:
        arbitrary_types_allowed = True

sessions: Dict[str, Session_model] = {}

codecs_to_libary = {
    'h264': 'libx264',
    'hevc': 'libx265',
    'vp9': 'libvpx-vp9',
}

class Stream_index(BaseModel):
    index: int
    group_index: int

class Transcoder:

    def __init__(self, settings: Transcode_settings, metadata: Dict):
        self.settings = settings
        self.metadata = metadata
        self.video_stream = self.get_video_stream()
        self.has_subtitle = False
        self.ffmpeg_args = None
        self.temp_folder = None

    async def start(self, send_data_callback=None) -> Union[bool, bytes]:
        if self.settings.session in sessions:
            return True
        self.temp_folder = self.create_temp_folder()
        self.set_ffmpeg_args()
        
        args = self.to_subprocess_arguments()
        logging.debug(f'FFmpeg start args: {" ".join(args)}')
        self.process = await asyncio.create_subprocess_exec(
            os.path.join(config.data.play.ffmpeg_folder, 'ffmpeg'),
            *args,
            env=self.subprocess_env(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        logging.debug('Waiting for media')
        try:
            ready = await asyncio.wait_for(self.wait_for_media(), timeout=10)
        except asyncio.TimeoutError:
            logging.error('Failed to create media, gave up waiting')
            self.process.terminate()
            return False

        if ready:
            self.register_session()
            return True
        return False

    def ffmpeg_extend_args(self) -> None:
        pass

    def ffmpeg_change_args(self) -> None:
        pass

    async def wait_for_media(self) -> bool:
        pass
    
    def close(self) -> None:
        pass

    @property
    def media_path(self) -> str:
        pass

    @property
    def media_name(self) -> str:
        pass

    def register_session(self):
        loop = asyncio.get_event_loop()
        logging.info(f'Register session {self.settings.session}')
        sessions[self.settings.session] = Session_model(
            process=self.process,
            temp_folder=self.temp_folder,
            call_later=loop.call_later(
                config.data.play.session_timeout,
                close_session_callback,
                self.settings.session
            ),
        )

    def set_ffmpeg_args(self) -> None:
        args = [
            {'-analyzeduration': '20000000'},
            {'-probesize': '20000000'},
            {'-i': self.metadata['format']['filename']},
            {'-y': None},
            {'-loglevel': 'quiet'},
            {'-map': '0:v:0'},
            {'-preset:0': config.data.play.ffmpeg_preset},
            {'-force_key_frames:0': 'expr:gte(t,n_forced*1)'},
            {'-c:a': 'aac'},
        ]
        if self.settings.start_time:
            args.insert(0, {'-ss': str(self.settings.start_time)})
            
        if self.settings.audio_channels:
            args.extend([{'-ac': str(self.settings.audio_channels)}])
        elif self.settings.audio_channels_fix: 
            # Fix for hls eac3 or ac3 not playing or just no audio
            a = self.stream_index_by_lang('audio', self.settings.audio_lang)
            if a:
                args.append({'-ac': str(self.metadata['streams'][a.index]['channels'])})
        self.ffmpeg_args = args
        self.set_subtitle()
        self.set_video_codec()
        self.set_pix_format()
        self.set_audio()
        self.set_scale()
        self.ffmpeg_extend_args()

    def set_video_codec(self):
        codec = codecs_to_libary[self.settings.transcode_codec]
        
        width = self.settings.width or self.video_stream['width']

        crf = '23'
        if codec == 'libx264':
            crf = '26'
            if width >= 3840:
                crf = '18'
            elif width >= 1920:
                crf = '19'
        elif codec == 'libx265':
            crf = '31'
            if width >= 3840:
                crf = '18'
            elif width >= 3840:
                crf = '20'
            elif width >= 1920:
                crf = '22'
        elif codec == 'libvpx-vp9':
            crf = '34'
            if width >= 3840:
                crf = '15'
            elif width >= 2560:
                crf = '24'
            elif width >= 1920:
                crf = '31'

        self.ffmpeg_args.append({'-crf': crf})
        self.ffmpeg_args.append({'-c:v': codec})
        if (codec == 'lib264'):
            self.ffmpeg_args.append({'-x264opts:0': 'subme=0:me_range=4:rc_lookahead=10:me=hex:8x8dct=0:partitions=none'})
        elif (codec == 'libx265'):
            self.ffmpeg_args.append({'-tag:v': 'hvc1'})

    def set_pix_format(self):
        if self.video_stream['pix_fmt'] in self.settings.supported_pixel_formats:
            self.ffmpeg_args.append({'-pix_fmt': self.video_stream['pix_fmt']})
        else:
            self.ffmpeg_args.append({'-pix_fmt': self.settings.transcode_pixel_format})

    def set_scale(self):    
        if self.settings.width and int(self.settings.width) < self.video_stream['width']:
            # keeps the aspect ratio for the height
            self.ffmpeg_args.append({'-filter:v': f'scale=width={self.settings.width}:height=-2'})

    def set_audio(self):
        arg = {'-map': '0:a:0'}
        if self.settings.audio_lang:
            sub_index = self.stream_index_by_lang('audio', self.settings.audio_lang)
            if sub_index:
                arg = {'-map': f'0:a:{sub_index.group_index}'}
        self.ffmpeg_args.append(arg)

    def stream_index_by_lang(self, codec_type: str, lang: str) -> Stream_index:
        logging.info(f'Looking for {codec_type} with language {lang}')
        group_index = -1
        langs = []
        lang = '' if lang == None else lang
        index = None
        if ':' in lang:
            lang, index = lang.split(':')
            index = int(index)
            if index <= (len(self.metadata['streams']) - 1):
                stream = self.metadata['streams'][index]
                if 'tags' not in stream:
                    index = None
                else:
                    l = stream['tags'].get('language') or stream['tags'].get('title')
                    if stream['codec_type'] != codec_type or l.lower() != lang.lower():
                        index = None
            else:
                index = None
        for i, stream in enumerate(self.metadata['streams']):
            if stream['codec_type'] == codec_type:
                group_index += 1
                if lang == '':
                    return Stream_index(index=i, group_index=group_index)
                if 'tags' in stream:
                    l = stream['tags'].get('language') or stream['tags'].get('title')
                    if not l:
                        continue
                    langs.append(l)
                    if not index or stream['index'] == index:
                        if l.lower() == lang.lower():
                            return Stream_index(index=i, group_index=group_index)
        logging.warning(f'Found no {codec_type} with language: {lang}')
        logging.warning(f'Available {codec_type}: {", ".join(langs)}')

    def set_subtitle(self):
        import subprocess
        args = self.get_subtitle_args()
        if not args:
            return False
        subtitle_file = os.path.join(
            config.data.play.temp_folder,
            f'{self.settings.session}.ass'
        )
        args.append(subtitle_file)
        process = subprocess.Popen(
            args,
            env=self.subprocess_env(),
        )
        r = process.wait()
        if r != 0:
            logging.warning('Subtitle file could not be saved!')
            return False
        logging.info(f'Subtitle file saved to: {subtitle_file}')
        self.ffmpeg_args.insert(
            self.ffmpeg_args.index({'-y': None})+1, 
            {'-vf': f'subtitles={subtitle_file}'}
        )
        self.has_subtitle = True

    def get_subtitle_args(self) -> Dict[str, str]:
        if not self.settings.subtitle_lang:
            return
        logging.debug(f'Looking for subtitle language: {self.settings.subtitle_lang}')
        sub_index = self.stream_index_by_lang('subtitle', self.settings.subtitle_lang)
        if not sub_index:
            return
        args = [
            os.path.join(config.data.play.ffmpeg_folder, 'ffmpeg'),
            '-i', self.metadata['format']['filename'],
            '-y',
            '-vn',
            '-an',
            '-c:s', 'ass',
            '-map', f'0:s:{sub_index.group_index}'
        ]    
        if self.settings.start_time:
            args.insert(1, '-ss')
            args.insert(2, str(self.settings.start_time))
        logging.debug(f'Subtitle args: {" ".join(args)}')
        return args

    def to_subprocess_arguments(self) -> List[str]:
        l = []
        for a in self.ffmpeg_args:
            for key, value in a.items():
                l.append(key)
                if value:
                    l.append(value)
        return l

    def get_video_stream(self) -> Dict:
        for stream in self.metadata['streams']:
            if stream['codec_type'] == 'video':
                return stream        
        if not stream:
            raise Exception('No video stream')

    def find_ffmpeg_arg(self, key):
        for a in self.ffmpeg_args:
            if key in a:
                return a[key]

    def change_ffmpeg_arg(self, key, new_value):
        for a in self.ffmpeg_args:
            if key in a:
                a[key] = new_value
                break

    def create_temp_folder(self):
        temp_folder = os.path.join(config.data.play.temp_folder, self.settings.session)
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        return temp_folder

    def subprocess_env(self) -> Dict:
        env = {}
        if config.data.play.ffmpeg_logfile:
            env['FFREPORT'] = f'file=\'{config.data.play.ffmpeg_logfile}\':level={config.data.play.ffmpeg_loglevel}'
        return env

def close_session_callback(session):
    close_session(session)

def close_session(session):
    logging.debug(f'Closing session: {session}')
    if session not in sessions:
        return
    s = sessions[session]
    try:
        s.process.kill()
    except:
        pass
    try:
        if s.temp_folder:
            if os.path.exists(s.temp_folder):
                shutil.rmtree(s.temp_folder)
            else:
                logging.warning(f'Path: {s.temp_folder} not found, can\'t delete it')  
    except:
        pass          
    s.call_later.cancel()
    del sessions[session]