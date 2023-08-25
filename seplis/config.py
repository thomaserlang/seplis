import os, pathlib
from typing import Literal
from pydantic_core.core_schema import FieldValidationInfo
from typing_extensions import Annotated
from pydantic import AnyHttpUrl, BaseModel, Field, conint, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

class ConfigRedisModel(BaseModel):
    ip: str = '127.0.0.1'
    host: Annotated[str | None, Field(validate_default=True)] = None
    port: int = 6379
    db: conint(ge=0, le=15) = 0
    sentinel: list[tuple[str, int]] = None
    master_name: str = 'mymaster'
    password: str | None = None
    queue_name: str = 'seplis:queue'
    job_completion_wait: int = 0
    
    @field_validator('host')
    @classmethod
    def default_host(cls, v: str | None, info: FieldValidationInfo):
        return v or info.data['ip']
    

class ConfigElasticsearch(BaseModel):
    host: str | list[str] = 'http://127.0.0.1:9200'
    user: str | None = None
    password: str | None = None
    verify_certs: bool = True
    index_prefix: str = 'seplis_'


class ConfigAPIModel(BaseModel):
    database: str = 'mariadb+pymysql://root:123456@127.0.0.1:3306/seplis'
    database_test: str = 'mariadb+pymysql://root:123456@127.0.0.1:3306/seplis_test'
    database_read_timeout: int = 5
    redis: ConfigRedisModel = ConfigRedisModel()
    elasticsearch: ConfigElasticsearch = ConfigElasticsearch()
    port: int = 8002
    max_workers: int = 5
    image_url: AnyHttpUrl = 'https://images.seplis.net'
    base_url: AnyHttpUrl = 'https://api.seplis.net'
    storitch_host: AnyHttpUrl | None = None
    storitch_api_key: str = ''


class ConfigWebModel(BaseModel):
    url: AnyHttpUrl | None = None
    cookie_secret: str | None = None
    port: int = 8001
    chromecast_appid: str = 'EA4A67C4'


class ConfigLoggingModel(BaseModel):
    level: Literal['notset', 'debug', 'info', 'warn', 'error', 'critical'] = 'warn'
    path: pathlib.Path = None
    max_size: int = 100 * 1000 * 1000 # ~ 95 mb
    num_backups: int = 10


class ConfigClientModel(BaseModel):
    access_token: str | None = None
    thetvdb: str | None = None
    themoviedb: str | None = None
    id: str | None = None
    validate_cert: bool = True
    api_url: AnyHttpUrl = 'https://api.seplis.net'
    public_api_url: Annotated[str | None, Field(validate_default=True)] = None

    @field_validator('public_api_url')
    @classmethod
    def default_public_api_url(cls, v: str | None, info: FieldValidationInfo):
        return v or info.data['api_url']
    

class ConfigSMTPModel(BaseModel):
    server: str = '127.0.0.1'
    port: int = 25
    user: str | None = None
    password: str | None = None
    use_tls: bool = None
    from_email: str | None = None
    
    
class ConfigModel(BaseSettings):
    debug: bool = False
    test: bool = False
    ENVIRONMENT: str | None = None
    sentry_dsn: str | None = None
    data_dir: str = '~/.seplis'
    api: ConfigAPIModel = ConfigAPIModel()
    web: ConfigWebModel = ConfigWebModel()
    logging: ConfigLoggingModel = ConfigLoggingModel()
    client: ConfigClientModel = ConfigClientModel()
    smtp: ConfigSMTPModel = ConfigSMTPModel()

    model_config = SettingsConfigDict(
        env_prefix='seplis_',
        env_nested_delimiter='.',
        validate_assignment=True,
        case_sensitive=False,
    )
    

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