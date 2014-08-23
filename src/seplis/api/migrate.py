import alembic.config
import logging
import os
from alembic import context
from seplis.config import config, load
from alembic import command

def get_config():
    cfg = alembic.config.Config(os.path.dirname(os.path.abspath(__file__))+'/alembic.ini')
    cfg.set_main_option('script_location', 'seplis.api:migration')
    cfg.set_main_option('url', config['database'])
    return cfg

def upgrade():
    cfg = get_config()
    command.upgrade(cfg, 'head')

if __name__ == '__main__':
    load()
    upgrade()
