

from seplis import config
from seplis.logger_utils import set_logger

set_logger(f'web-{config.web.port}.log')

