import os, pathlib
from typing import List, Literal, Optional, Tuple
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, DirectoryPath, EmailStr, conint, validator
import yaml, tempfile

class ConfigRedisModel(BaseSettings):
    ip: str = '127.0.0.1'
    port: int = 6379
    db: conint(ge=0, le=15) = 0
    sentinel: Optional[List[Tuple[str, int]]]
    password: Optional[str]

    class Config:
        env_prefix = 'seplis_redis_'

class ConfigAPIModel(BaseSettings):
    database = 'mariadb+pymysql://root:123456@127.0.0.1:3306/seplis'
    database_test = 'mariadb+pymysql://root:123456@127.0.0.1:3306/seplis_test'
    database_read_timeout = 5
    redis = ConfigRedisModel()
    elasticsearch: Optional[AnyHttpUrl]
    port = 8002
    max_workers = 5
    image_url: Optional[AnyHttpUrl] = 'https://images.seplis.net'
    base_url: Optional[AnyHttpUrl] = 'https://seplis.net'
    storitch: Optional[AnyHttpUrl]

    class Config:
        env_prefix = 'seplis_api_'
        env_nested_delimiter = '_'
        validate_assignment = True
        case_sensitive = False

class ConfigWebModel(BaseSettings):
    url: Optional[AnyHttpUrl]
    cookie_secret: Optional[str]
    port = 8001
    chromecast_appid = 'EA4A67C4'

    class Config:
        env_prefix = 'seplis_web_'

class ConfigLoggingModel(BaseSettings):
    level: Literal['notset', 'debug', 'info', 'warn', 'error', 'critical'] = 'warn'
    path: Optional[DirectoryPath]
    max_size: int = 100 * 1000 * 1000 # ~ 95 mb
    num_backups = 10
    
    class Config:
        env_prefix = 'seplis_logging_'

class ConfigClientModel(BaseSettings):
    access_token: Optional[str]
    thetvdb: Optional[str]
    themoviedb: Optional[str]
    id: Optional[str]
    validate_cert = True
    api_url: AnyHttpUrl = 'https://api.seplis.net'
    public_api_url: Optional[AnyHttpUrl]

    @validator('public_api_url', pre=True, always=True)
    def default_ts_modified(cls, v, *, values, **kwargs):
        return v or values['api_url']

    class Config:
        env_prefix = 'seplis_client_'

class ConfigPlayScanModel(BaseModel):
    type: Literal['series', 'movies']
    path: DirectoryPath

class ConfigPlayModel(BaseSettings):
    database: Optional[str]
    secret: Optional[str]
    scan: Optional[List[ConfigPlayScanModel]]
    media_types: List[str] = ['mp4', 'mkv', 'avi', 'mpg']
    ffmpeg_folder: pathlib.Path = '/usr/src/ffmpeg'
    ffmpeg_threads = 4
    ffmpeg_loglevel = '8'
    ffmpeg_logfile: Optional[pathlib.Path]
    ffmpeg_preset: Literal['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster', 'veryfast', 'superfast', 'ultrafast'] = 'veryfast' 
    ffmpeg_enable_codec_copy = False
    ffmpeg_hls_segment_type: Literal['mpegts', 'fmp4'] = 'fmp4'
    port = 8003
    temp_folder: DirectoryPath = os.path.join(tempfile.gettempdir(), 'seplis_play')
    segment_time = 5
    session_timeout = 5 # Timeout for HLS sessions

    class Config:
        env_prefix = 'seplis_play_'

class ConfigSMTPModel(BaseSettings):
    server = '127.0.0.1'
    port = 25
    user: Optional[str]
    password: Optional[str]
    use_tls: Optional[bool]
    from_email: Optional[str]

    class Config:
        env_prefix = 'seplis_smtp_'
    
class ConfigModel(BaseSettings):
    debug = False
    sentry_dsn: Optional[str]
    data_dir = '~/.seplis'
    api = ConfigAPIModel()
    web = ConfigWebModel()
    logging = ConfigLoggingModel()
    client = ConfigClientModel()
    play = ConfigPlayModel()
    smtp = ConfigSMTPModel()

    class Config:
        env_prefix = 'seplis_'
        env_nested_delimiter = '_'
        validate_assignment = True
        case_sensitive = False

class Config:
    def __init__(self):
        self.data = ConfigModel()
config = Config()

def load(path=None):
    default_paths = [
        '~/seplis.yaml',
        './seplis.yaml',
        '../seplis.yaml',
        '../../seplis.yaml',
        '../../../seplis.yaml',
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
        raise Exception(f'Config: "{path}" could not be found.')
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
        config.data = ConfigModel(**data)

    if config.data.play.temp_folder:
        os.makedirs(config.data.play.temp_folder, exist_ok=True)
