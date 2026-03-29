import os
import sys
from pathlib import Path
from typing import Annotated, Literal

from loguru import logger
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationInfo, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class ConfigRedisModel(BaseModel):
    ip: str = '127.0.0.1'
    host: Annotated[str, Field(validate_default=True)] = ''
    port: int = 6379
    db: Annotated[int, Field(ge=0, le=15)] = 0
    sentinel: list[tuple[str, int]] | None = None
    master_name: str = 'mymaster'
    password: str | None = None
    queue_name: str = 'seplis:queue'
    job_completion_wait: int = 0

    @field_validator('host')
    @classmethod
    def default_host(cls, v: str | None, info: ValidationInfo) -> str | None:
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
    image_url: AnyHttpUrl = AnyHttpUrl('https://images.seplis.net')
    base_url: AnyHttpUrl = AnyHttpUrl('https://api.seplis.net')
    storitch_host: AnyHttpUrl | None = None
    storitch_api_key: str = ''


class ConfigWebModel(BaseModel):
    url: AnyHttpUrl | None = None
    cookie_secret: str | None = None
    port: int = 8001
    chromecast_appid: str = 'EA4A67C4'


class ConfigLoggingModel(BaseModel):
    level: Literal['notset', 'debug', 'info', 'warn', 'error', 'critical'] = 'warn'
    path: Path | None = None
    max_size: int = 100 * 1000 * 1000  # ~ 95 mb
    num_backups: int = 10


class ConfigClientModel(BaseModel):
    access_token: str | None = None
    thetvdb: str | None = None
    themoviedb: str | None = None
    id: str | None = None
    validate_cert: bool = True
    api_url: AnyHttpUrl = AnyHttpUrl('https://api.seplis.net')
    public_api_url: Annotated[str | None, Field(validate_default=True)] = None

    @field_validator('public_api_url')
    @classmethod
    def default_public_api_url(cls, v: str | None, info: ValidationInfo) -> str | None:
        return v or info.data['api_url']


class ConfigSMTPModel(BaseModel):
    server: str = '127.0.0.1'
    port: int = 25
    user: str | None = None
    password: str | None = None
    use_tls: bool | None = None
    from_email: str | None = None


def get_config_path() -> Path | None:
    path: Path | None = None
    if os.environ.get('SEPLIS__CONFIG', None):
        path = Path(os.environ['SEPLIS__CONFIG'])
    if os.environ.get('SEPLIS_CONFIG', None):
        path = Path(os.environ['SEPLIS_CONFIG'])

    if not path:
        default_paths = (Path(__file__).parent / '../seplis.yaml',)

        if 'pytest' in sys.modules:
            default_paths = (Path(__file__).parent / '../seplis-test.yml',)

        for p in default_paths:
            if p.exists():
                path = p
                break
    if not path:
        return None

    path = path.expanduser()
    if not path.exists():
        raise Exception(f'Config file does not exist: {path}')

    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format='<blue>{message}</blue>',
    )
    logger.info(f'Config: {path}')
    return path


class ConfigModel(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='seplis__',
        env_nested_delimiter='__',
        validate_assignment=True,
        case_sensitive=False,
        extra='forbid',
        yaml_file=get_config_path(),
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )

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


config = ConfigModel()
