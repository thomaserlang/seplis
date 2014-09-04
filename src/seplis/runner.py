import logging
import sys
import aaargh
from seplis.logger import logger

app = aaargh.App(description='SEPLIS')

app.arg('--config', help='Path to the config file.', default=None)

@app.cmd()
@app.cmd_arg('-p', '--port', type=int, default=8001)
def web(config, port):
    import seplis
    seplis.config_load(config)
    if port != 8001:
        seplis.config['web']['port'] = port            
    import seplis.web.app
    seplis.web.app.main()

@app.cmd()
@app.cmd_arg('-p', '--port', type=int, default=8002)
@app.cmd_arg('-rc', '--rebuild_cache', type=bool, default=False)
def api(config, port, rebuild_cache):
    import seplis
    seplis.config_load(config)
    if port != 8002:
        seplis.config['api']['port'] = port
    if rebuild_cache:
        import seplis.api.rebuild_cache
        seplis.api.rebuild_cache.main() 
    import seplis.api.app
    seplis.api.app.main()

@app.cmd()
def upgrade(config):
    import seplis
    seplis.config_load(config)
    import seplis.api.migrate
    seplis.api.migrate.upgrade()

@app.cmd()
def rebuild_cache(config):
    seplis.config_load(config)
    logger.set_logger('rebuild_cache.log')
    import seplis.api.rebuild_cache
    seplis.api.rebuild_cache.main()

@app.cmd()
def indexer_update(config):
    import seplis
    seplis.config_load(config)
    logger.set_logger('indexer_update.log')
    import seplis.indexer
    indexer = seplis.indexer.Show_indexer(
        seplis.config['api']['url'],
        access_token=seplis.config['client']['access_token'],
    )
    indexer.update()  

def main():
    app.run()

if __name__ == "__main__":
    main()