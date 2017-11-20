import os
import os.path
import yaml
import tempfile
from seplis import schemas

config = {
    'debug': False,
    'sentry_dsn': None,
    'data_dir': '~/.seplis',
    'api': {
        'database': 'sqlite:///seplis.db',    
        'redis': {
            'ip': '127.0.0.1',
            'port': 6379,
        },
        'elasticsearch': 'localhost:9200',
        'storitch': None,
        'port': 8002,
        'max_workers': 5,
        'image_url': 'https://images.seplis.net',
        'base_url': 'https://api.seplis.net',
    },
    'web': {
        'url': 'https://seplis.net',
        'cookie_secret': 'CHANGE_ME',
        'port': 8001,
        'chromecast_appid': 'AA4C338C',
    },
    'logging': {
        'level': 'warning',
        'path': None,
        'max_size': 100 * 1000 * 1000,# ~ 95 mb
        'num_backups': 10,
    },
    'client': {
        'access_token': None,
        'thetvdb': None,
        'id': 'CHANGE_ME',
        'validate_cert': True,
        'api_url': 'https://api.seplis.net',
        'public_api_url': None,
    },
    'play': {
        'database': 'sqlite:///seplis-play.db',
        'secret': None,
        'scan': None,
        'media_types': [
            'mp4',
            'mkv',
            'avi',
            'mpg',
        ],

        'ffmpeg_folder': '/usr/src/ffmpeg/',
        'ffmpeg_threads': 1,
        'ffmpeg_loglevel': '8',
        'ffmpeg_logfile': None,

        'port': 8003,
        'temp_folder': os.path.join(tempfile.gettempdir(), 'seplis-play'),
        'segment_time': 2,
        'session_timeout': 5, # Timeout for HLS sessions
        'x-accel': False,
    },
}

def load(path=None):
    default_paths = [
        '~/seplis.yaml',
        './seplis.yaml',
        '/etc/seplis/seplis.yaml',
        '/etc/seplis.yaml',
    ]
    if not path:
        path = os.environ.get('SEPLIS_CONFIG', None)
        if not path:
            for p in default_paths:
                p = os.path.expanduser(p)
                if os.path.isfile(p):
                    path = p
                    break
    if not path:
        raise Exception('No config file specified.')
    if not os.path.isfile(path):
        raise Exception('Config: "{}" could not be found.'.format(path))
    with open(path) as f:
        data = yaml.load(f)
    for key in data:
        if key in config:
            if isinstance(config[key], dict):
                config[key].update(data[key])
            else:
                config[key] = data[key]
    if config['play']['scan']:# validate the play scan items
        schemas.Config_play_scan(
            config['play']['scan']
        )
    if config['web']['url']:
        config['web']['url'] = config['web']['url'].rstrip('/')
    if config['api']['image_url']:
        config['api']['image_url'] = config['api']['image_url'].rstrip('/')
    if config['client']['api_url']:
        config['client']['api_url'] = config['client']['api_url'].rstrip('/')
    if not config['client']['public_api_url']:
        config['client']['public_api_url'] = config['client']['api_url']
    else:
        if config['client']['public_api_url']:
            config['client']['public_api_url'] = \
                config['client']['public_api_url'].rstrip('/')

    if config['play']['ffmpeg_logfile']:
        ps = os.path.split(config['play']['ffmpeg_logfile'])
        if not ps[0]:
            if config['logging']['path']:
                config['play']['ffmpeg_logfile'] = os.path.join(
                    config['logging']['path'],
                    config['play']['ffmpeg_logfile'],
                )
            else:
                config['play']['ffmpeg_logfile'] = None
    if config['play']['temp_folder']:
        if not os.path.exists(config['play']['temp_folder']):
            os.makedirs(config['play']['temp_folder'])