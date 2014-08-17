import logging
import sys
import aaargh
from seplis import seplis_config, seplis_load
from seplis.logger import logger

app = aaargh.App(description='SEPLIS')

app.arg('--config', help='Path to the config file.', default=None)

@app.cmd()
@app.cmd_arg('-p', '--port', type=int, default=8001)
def web(config, port):
    seplis_load(config)
    if port != 8001:
        seplis_config['web']['port'] = port            
    import seplis.web.app
    seplis.web.app.main()

@app.cmd()
@app.cmd_arg('-p', '--port', type=int, default=8002)
@app.cmd_arg('-rc', '--rebuild_cache', type=bool, default=False)
def api(config, port, rebuild_cache):
    seplis_load(config)
    if port != 8002:
        seplis_config['api']['port'] = port
    if rebuild_cache:
        import seplis.api.rebuild_cache
        seplis.api.rebuild_cache.main() 
    import seplis.api.app
    seplis.api.app.main()

@app.cmd()
def upgrade(config):
    seplis_load(config)
    logger.set_logger('upgrade.log')
    import seplis.api.migrate
    seplis.api.migrate.upgrade()

@app.cmd()
def rebuild_cache(config):
    seplis_load(config)
    logger.set_logger('rebuild_cache.log')
    import seplis.api.rebuild_cache
    seplis.api.rebuild_cache.main()

if __name__ == "__main__":
    app.run()