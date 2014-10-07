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
    logger.set_logger('upgrade.log', to_sentry=True)
    import seplis.api.migrate
    try:
        seplis.api.migrate.upgrade()
    except:
        logging.exception('upgrade')

@app.cmd()
def downgrade(config):
    import seplis
    seplis.config_load(config)
    logger.set_logger('downgrade.log', to_sentry=True)
    import seplis.api.migrate
    try:
        seplis.api.migrate.downgrade()
    except:
        logging.exception('downgrade')

@app.cmd()
def rebuild_cache(config):
    import seplis
    seplis.config_load(config)
    logger.set_logger('rebuild_cache.log', to_sentry=True)
    import seplis.api.rebuild_cache
    try:
        seplis.api.rebuild_cache.main()
    except:
        logging.exception('rebuild_cache')

@app.cmd()
def update_shows(config):
    import seplis
    seplis.config_load(config)
    logger.set_logger('indexer_update_shows.log', to_sentry=True)
    try:
        indexer = seplis.Show_indexer(
            seplis.config['api']['url'],
            access_token=seplis.config['client']['access_token'],
        )
        indexer.update()
    except:
        logging.exception('indexer_update_shows')

@app.cmd()
@app.cmd_arg('-id', '--show_id', type=int, help='The id of the show')
def update_show(config, show_id):
    import seplis
    seplis.config_load(config)
    logger.set_logger('indexer_update_show.log', to_sentry=True)
    try:
        indexer = seplis.Show_indexer(
            seplis.config['api']['url'],
            access_token=seplis.config['client']['access_token'],
        )
        indexer.update_show(show_id)
    except:
        logging.exception('indexer_update_show')

@app.cmd()
@app.cmd_arg('--from_id', type=int, default=1)
def update_shows_all(config, from_id):
    import seplis
    seplis.config_load(config)
    logger.set_logger('indexer_update_shows_all.log', to_sentry=True)
    indexer = seplis.Show_indexer(
        url=seplis.config['api']['url'], 
        access_token=seplis.config['client']['access_token']
    )
    try:
        shows = indexer.get('/shows', {
            'sort': 'id',
            'per_page': 500,
            'q': 'id:[{} TO *]'.format(from_id)
        })
        for show in shows.all():
            indexer.update_show(show['id'])
    except:
        logging.exception('update_shows_all')

@app.cmd()
def worker(config):
    import seplis
    seplis.config_load(config)
    logger.set_logger('worker.log')
    import seplis.tasks.worker
    seplis.tasks.worker.main()

def main():
    app.run()

if __name__ == "__main__":
    main()