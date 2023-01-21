import pytest_asyncio
import tempfile
from seplis import config, config_load
from seplis.logger import logger, set_logger


def run_file(file_):
    import subprocess
    subprocess.call(['pytest', '--tb=short', str(file_)])


@pytest_asyncio.fixture(scope='function')
async def play_db_test():
    from seplis.play.database import database
    from seplis.play import scan
    config_load()
    set_logger('play_test')
    config.data.test = True
    config.data.play.server_id = '123'
    with tempfile.TemporaryDirectory() as dir:
        config.data.play.database = f'sqlite:///{dir}/db.sqlite'
        scan.upgrade_scan_db()
        database.setup()
        yield database
        await database.close()