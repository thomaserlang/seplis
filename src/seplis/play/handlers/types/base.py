import os
import logging
from seplis import config

def subprocess_env():
    env = {}
    if config.data.play.ffmpeg_logfile:
        env['FFREPORT'] = f'file=\'{config.data.play.ffmpeg_logfile}\':level={config.data.play.ffmpeg_loglevel}'
    return env

def ffmpeg_base_args(handler, settings, metadata):
    args = [
        {os.path.join(config.data.play.ffmpeg_folder, 'ffmpeg'): None},
        {'-i': metadata['format']['filename']},
        {'-y': None},
        {'-loglevel': 'quiet'},
        {'-crf:0': '16'},
        {'-map': '0:v:0'},
        {'-preset:0': config.data.play.ffmpeg_preset},
        {'-x264opts:0': 'subme=0:me_range=4:rc_lookahead=10:me=hex:8x8dct=0:partitions=none'},
        {'-force_key_frames:0': 'expr:gte(t,n_forced*1)'},
        {'-c:a': 'aac'},
        {'-pix_fmt': settings['transcode_pixel_format']},
    ]
    start_time = handler.get_argument('start_time', None)
    if start_time:
        args.insert(1, {'-ss': start_time})
    has_subtitle = set_subtitle(handler, metadata, args)
    set_video_codec(settings, metadata, has_subtitle, args)
    set_audio(handler, metadata, args)
    return args

def to_subprocess_arguments(args):
    l = []
    for a in args:
        for key, value in a.items():
            l.append(key)
            if value:
                l.append(value)
    return l

def find_ffmpeg_arg(key, ffmpeg_args):
    for a in ffmpeg_args:
        if key in a:
            return a[key]

def change_ffmpeg_arg(key, ffmpeg_args, new_value):
    for a in ffmpeg_args:
        if key in a:
            a[key] = new_value

def set_video_codec(settings, metadata, has_subtitle, ffmpeg_args):
    def video_stream():
        for stream in metadata['streams']:
            if stream['codec_type'] == 'video':
                return stream
    stream = video_stream()
    if not stream:
        raise Exception('No video stream')
    codec = settings['transcode_codec']
    if (settings['type'] == 'pipe') and \
        not has_subtitle and \
        stream['codec_name'] in settings['codec_names'] and \
        stream['pix_fmt'] in settings['pixel_formats']:
        codec = 'copy'
    ffmpeg_args.append({'-c:v': codec})

def set_audio(handler, metadata, ffmpeg_args):
    audio_lang = handler.get_argument('audio_lang', None)
    arg = {'-map': '0:a:0'}
    if audio_lang:
        sub_index = stream_index_by_lang(metadata, 'audio', audio_lang)
        if sub_index:
            arg = {'-map': '0:a:{}'.format(sub_index['group_index'])}
    ffmpeg_args.append(arg)

def set_subtitle(handler, metadata, ffmpeg_args):
    import subprocess
    args = get_subtitle_args(handler, metadata)
    if not args:
        return False
    session = handler.get_argument('session')
    subtitle_file = os.path.join(
        config.data.play.temp_folder,
        '{}.ass'.format(session)
    )
    args.append(subtitle_file)
    process = subprocess.Popen(
        args,
        env=subprocess_env(),
    )
    r = process.wait()
    if r != 0:
        logging.warning('Subtitle file could not be saved!')
        return False
    logging.info('Subtitle file saved to: {}'.format(subtitle_file))
    ffmpeg_args.insert(
        ffmpeg_args.index({'-y': None})+1, 
        {'-vf': 'subtitles={}'.format(subtitle_file)}
    )
    return True

def get_subtitle_args(handler, metadata):
    subtitle_lang = handler.get_argument('subtitle_lang', None)
    if not subtitle_lang:
        return
    logging.debug('Looking for subtitle language: {}'.format(subtitle_lang))
    sub_index = stream_index_by_lang(metadata, 'subtitle', subtitle_lang)
    if not sub_index:
        return
    args = [
        os.path.join(config.data.play.ffmpeg_folder, 'ffmpeg'),
        '-i', metadata['format']['filename'],
        '-y',
        '-vn',
        '-an',
        '-c:s', 'ass',
        '-map', '0:s:{}'.format(sub_index['group_index'])
    ]    
    start_time = handler.get_argument('start_time', None)
    if start_time:
        args.insert(1, '-ss')
        args.insert(2, str(start_time))
    logging.debug('Subtitle args: {}'.format(' '.join(args)))
    return args

from typing import TypedDict
class Stream_index(TypedDict):
    index: int
    group_index: int

def stream_index_by_lang(metadata, codec_type, lang) -> Stream_index:
    logging.info('Looking for {} with language {}'.format(codec_type, lang))
    group_index = -1
    langs = []
    index = None
    if ':' in lang:
        lang, index = lang.split(':')
        index = int(index)
        if index <= (len(metadata['streams']) - 1):
            stream = metadata['streams'][index]
            if 'tags' not in stream:
                index = None
            else:
                l = stream['tags'].get('language') or stream['tags'].get('title')
                if stream['codec_type'] != codec_type or l.lower() != lang.lower():
                    index = None
        else:
            index = None
    for i, stream in enumerate(metadata['streams']):
        if stream['codec_type'] == codec_type:
            group_index += 1
            if lang == '':
                return {
                    'index': i,
                    'group_index': group_index,
                }
            if 'tags' in stream:
                l = stream['tags'].get('language') or stream['tags'].get('title')
                if not l:
                    continue
                langs.append(l)
                if not index or stream['index'] == index:
                    if l.lower() == lang.lower():
                        return {
                            'index': i,
                            'group_index': group_index,
                        }
    logging.warning('Found no {} with language: {}'.format(codec_type, lang))
    logging.warning('Available {}: {}'.format(codec_type, ', '.join(langs)))