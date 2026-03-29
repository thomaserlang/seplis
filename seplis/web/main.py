

from seplis import config
from seplis.logger import set_logger

set_logger(f'web-{config.web.port}.log')

