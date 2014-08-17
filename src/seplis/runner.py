import logging
import sys
import aaargh
from seplis.config import config, load
from seplis.logger import logger

app = aaargh.App(description='SEPLIS')

app.arg('--config', help='Path to the config file.', default=None)

@app.cmd()
@app.cmd_arg('-p', '--port', type=int, default=8001)
def web(config, port):
    load(config)
    if port != 8001:
        config['web']['port'] = port            
    import seplis.web.app
    seplis.web.app.main()

@app.cmd()
@app.cmd_arg('-p', '--port', type=int, default=8002)
def api(config, port):
    load(config)
    if port != 8002:
        config['web']['port'] = port            
    import seplis.api.app
    seplis.api.app.main()

@app.cmd()
def upgrade(config):
    load(config)
    logger.set_logger('upgrade.log')
    import seplis.api.migrate
    seplis.api.migrate.upgrade()


if __name__ == "__main__":
    app.run()