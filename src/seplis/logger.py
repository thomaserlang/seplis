import logging, logging.handlers, os, sentry_sdk
from seplis.config import config
from tornado import log

class logger(object):

    @classmethod
    def set_logger(cls, filename, to_sentry=False):
        logger = logging.getLogger()
        logger.setLevel(config.data.logging.level.upper())
        logger.handlers = []
        format_ = log.LogFormatter(
            '[%(color)s%(levelname)s%(end_color)s %(asctime)s %(module)s:%(lineno)d]: %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        if config.data.logging.path:
            channel = logging.handlers.RotatingFileHandler(
                filename=os.path.join(config.data.logging.path, filename),
                maxBytes=config.data.logging.max_size,
                backupCount=config.data.logging.num_backups,
            )
            channel.setFormatter(format_)
            logger.addHandler(channel)
        else:# send to console instead of file
            channel = logging.StreamHandler()
            channel.setFormatter(format_)
            logger.addHandler(channel)
        if to_sentry and config.data.sentry_dsn:
            sentry_sdk.init(
                dsn=config.data.sentry_dsn,
            )