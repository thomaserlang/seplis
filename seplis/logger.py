import logging, os, sentry_sdk
from seplis.config import config

logger = logging.getLogger('seplis')

logging.getLogger('urllib3').setLevel(logging.ERROR)

def set_logger(filename, to_sentry=True):
    logger.setLevel(config.data.logging.level.upper())
    glogger = logging.getLogger()
    glogger.handlers = []
    format_ = logging.Formatter(        
        fmt='[%(asctime)s.%(msecs)-3d] %(levelname)-8s %(message)s (%(filename)s:%(lineno)d)',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    if config.data.logging.path:
        channel = logging.handlers.RotatingFileHandler(
            filename=os.path.join(config.data.logging.path, filename),
            maxBytes=config.data.logging.max_size,
            backupCount=config.data.logging.num_backups,
        )
        channel.setFormatter(format_)
        glogger.addHandler(channel)
    else:# send to console instead of file
        channel = logging.StreamHandler()
        channel.setFormatter(format_)
        glogger.addHandler(channel)
    if to_sentry and config.data.sentry_dsn:
        sentry_sdk.init(
            dsn=config.data.sentry_dsn,
        )