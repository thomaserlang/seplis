import logging, logging.handlers, os, sentry_sdk
from seplis.config import config

class logger(object):

    @classmethod
    def set_logger(cls, filename, to_sentry=False):
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, config['logging']['level'].upper()))
        logger.handlers = []
        format_ = logging.Formatter(
            '[%(levelname)s %(asctime)s.%(msecs)d %(module)s:%(lineno)d]: %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        if config['logging']['path']:
            channel = logging.handlers.RotatingFileHandler(
                filename=os.path.join(config['logging']['path'], filename),
                maxBytes=config['logging']['max_size'],
                backupCount=config['logging']['num_backups']
            )
            channel.setFormatter(format_)
            logger.addHandler(channel)
        else:# send to console instead of file
            channel = logging.StreamHandler()
            channel.setFormatter(format_)
            logger.addHandler(channel)
        if to_sentry and config['sentry_dsn']:
            sentry_sdk.init(
                dsn=config['sentry_dsn'],
            )