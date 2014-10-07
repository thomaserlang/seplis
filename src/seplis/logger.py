import logging
import logging.handlers
import os
from seplis.config import config
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

class logger(object):

    @classmethod
    def set_logger(cls, filename, to_sentry=False):
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, config['logging']['level'].upper()))
        if config['logging']['path']:
            channel = logging.handlers.RotatingFileHandler(
                filename=os.path.join(config['logging']['path'], filename),
                maxBytes=config['logging']['max_size'],
                backupCount=config['logging']['num_backups']
            )
            channel.setFormatter(logging.Formatter('[%(levelname)s %(asctime)s.%(msecs)d %(module)s:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            logger.addHandler(channel)
        if not logger.handlers:# send to console instead of file
            channel = logging.StreamHandler()
            channel.setFormatter(logging.Formatter('[%(levelname)s %(asctime)s.%(msecs)d %(module)s:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            logger.addHandler(channel)
        if to_sentry and config['sentry_dsn']:
            handler = SentryHandler(
                config['sentry_dsn']
            )
            handler.setLevel('ERROR')
            logger.addHandler(handler)