import os, pathlib
from typing import List, Literal, Optional, Tuple, Union
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, conint, validator, DirectoryPath
import yaml, tempfile

class ConfigRedisModel(BaseModel):
    ip: str = '127.0.0.1'
    host: str = None
    port: int = 6379
    db: conint(ge=0, le=15) = 0
    sentinel: Optional[List[Tuple[str, int]]]
    master_name = 'mymaster'
    password: Optional[str]
    queue_name = 'seplis:queue'
    job_completion_wait = 0
    
    @validator('host', pre=True, always=True)
    def default_host(cls, v, *, values, **kwargs):
        return v or values['ip']

class ConfigElasticsearch(BaseModel):
    host: Union[str, List[str]] = 'http://127.0.0.1:9200'
    user: Optional[str]
    password: Optional[str]
    verify_certs = True
    index_prefix = 'seplis_'

class ConfigAPIModel(BaseModel):
    database = 'mariadb+pymysql://root:123456@127.0.0.1:3306/seplis'
    database_test = 'mariadb+pymysql://root:123456@127.0.0.1:3306/seplis_test'
    database_read_timeout = 5
    redis = ConfigRedisModel()
    elasticsearch = ConfigElasticsearch()
    port = 8002
    max_workers = 5
    image_url: Optional[AnyHttpUrl] = 'https://images.seplis.net'
    base_url: Optional[AnyHttpUrl] = 'https://api.seplis.net'
    storitch: Optional[AnyHttpUrl]

class ConfigWebModel(BaseModel):
    url: Optional[AnyHttpUrl]
    cookie_secret: Optional[str]
    port = 8001
    chromecast_appid = 'EA4A67C4'

class ConfigLoggingModel(BaseModel):
    level: Literal['notset', 'debug', 'info', 'warn', 'error', 'critical'] = 'warn'
    path: Optional[pathlib.Path]
    max_size: int = 100 * 1000 * 1000 # ~ 95 mb
    num_backups = 10

class ConfigClientModel(BaseModel):
    access_token: Optional[str]
    thetvdb: Optional[str]
    themoviedb: Optional[str]
    id: Optional[str]
    validate_cert = True
    api_url: AnyHttpUrl = 'https://api.seplis.net'
    public_api_url: Optional[AnyHttpUrl]

    @validator('public_api_url', pre=True, always=True)
    def default_public_api_url(cls, v, *, values, **kwargs):
        return v or values['api_url']

class ConfigPlayScanModel(BaseModel):
    type: Literal['series', 'movies']
    path: pathlib.Path
    make_thumbnails: bool = False

class ConfigPlayModel(BaseModel):
    database: Optional[str]
    secret: Optional[str]
    scan: Optional[List[ConfigPlayScanModel]]
    media_types: List[str] = ['mp4', 'mkv', 'avi', 'mpg']
    ffmpeg_folder: pathlib.Path = '/usr/src/ffmpeg'
    ffmpeg_loglevel = '8'
    ffmpeg_logfile: Optional[pathlib.Path]
    ffmpeg_preset: Literal['veryslow', 'slower', 'slow', 'medium', 'fast', 'faster', 'veryfast', 'superfast', 'ultrafast'] = 'veryfast' 
    port = 8003
    temp_folder: pathlib.Path = os.path.join(tempfile.gettempdir(), 'seplis_play')
    thumbnails_path: Optional[pathlib.Path]
    session_timeout = 10 # Timeout for HLS sessions
    server_id: str | None = None

class ConfigSMTPModel(BaseModel):
    server = '127.0.0.1'
    port = 25
    user: Optional[str]
    password: Optional[str]
    use_tls: Optional[bool]
    from_email: Optional[str]
    
class ConfigModel(BaseSettings):
    debug = False
    test = False
    ENVIRONMENT: Optional[str]
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
        env_nested_delimiter = '.'
        validate_assignment = True
        case_sensitive = False

class Config:
    def __init__(self):
        self.data = None
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
        if data:
            config.data = ConfigModel(**data)

    if config.data.play.temp_folder:
        try:
            os.makedirs(config.data.play.temp_folder, exist_ok=True)
        except:
            pass