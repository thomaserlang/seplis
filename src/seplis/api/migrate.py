import logging
import os
import alembic.config
from alembic import command
from seplis.config import config, load

def get_config():
    cfg = alembic.config.Config(os.path.dirname(os.path.abspath(__file__))+'/alembic.ini')
    cfg.set_main_option('script_location', 'seplis.api:migration')
    cfg.set_main_option('sqlalchemy.url', config.data.api.database)
    return cfg

def upgrade():
    cfg = get_config()
    command.upgrade(cfg, 'head')

if __name__ == '__main__':
    load()
    upgrade()
