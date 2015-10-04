import logging
import sys
import click
from seplis.logger import logger
from seplis import config

@click.group()
@click.option('--config', default=None, help='path to the config file')
@click.option('--log_path', '-lp', default=None, help='a folder to store the log files in')
@click.option('--log_level', '-ll', default=None, help='notset, debug, info, warning, error or critical')
def cli(config, logging_path, logging_level):
    import seplis
    seplis.config_load(config)
    if logging_path != None:
        seplis.config['logging']['path'] = logging_path
    if logging_level:
        seplis.config['logging']['level'] = logging_level

@cli.command()
@click.option('--port', '-p', default=config['web']['port'], help='the port')
def web(port):
    if port:
        config['web']['port'] = port            
    import seplis.web.app
    seplis.web.app.main()

@cli.command()
@click.option('--port', '-p', default=config['api']['port'], help='the port')
def api(port):
    if port:
        config['api']['port'] = port
    import seplis.api.app
    seplis.api.app.main()

@cli.command()
def upgrade():
    logger.set_logger('upgrade.log', to_sentry=True)
    import seplis.api.migrate
    try:
        seplis.api.migrate.upgrade()
    except:
        logging.exception('upgrade')

@cli.command()
def rebuild_cache():
    logger.set_logger('rebuild_cache.log', to_sentry=True)
    import seplis.api.rebuild_cache
    try:
        seplis.api.rebuild_cache.main()
    except:
        logging.exception('rebuild_cache')

@cli.command()
def update_shows():
    import seplis
    logger.set_logger('indexer_update_shows.log', to_sentry=True)
    try:
        indexer = seplis.Show_indexer(
            config['client']['api_url'],
            access_token=config['client']['access_token'],
        )
        indexer.update()
    except:
        logging.exception('indexer_update_shows')

@cli.command()
@click.argument('show_id')
def update_show(show_id):
    import seplis
    logger.set_logger('indexer_update_show.log', to_sentry=True)
    try:
        indexer = seplis.Show_indexer(
            config['client']['api_url'],
            access_token=config['client']['access_token'],
        )
        indexer.update_show(show_id)
    except:
        logging.exception('indexer_update_show')

@cli.command()
@click.option('--from_id', default=1, help='which show to start from')
def update_shows_all(from_id):
    import seplis
    logger.set_logger('indexer_update_shows_all.log', to_sentry=True)
    indexer = seplis.Show_indexer(
        url=config['client']['api_url'], 
        access_token=config['client']['access_token']
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

@cli.command()
def worker():
    logger.set_logger('worker.log')
    import seplis.tasks.worker
    try:
        seplis.tasks.worker.main()
    except:
        logging.exception('worker')

@cli.command()
@click.option('--disable_cleanup', is_flag=True, help='Disable cleanup after scan')
def play_scan(disable_cleanup):
    import seplis.play.scan
    try:
        seplis.play.scan.upgrade_scan_db()
    except:        
        logging.exception('play scan db upgrade')
        raise
    logger.set_logger('play_scan.log', to_sentry=True)
    seplis.play.scan.scan()
    if not disable_cleanup:
        seplis.play.scan.cleanup()

@cli.command()
def play_scan_watch():
    import seplis.play.scan_watch
    import seplis.play.scan
    try:
        seplis.play.scan.upgrade_scan_db()
    except:        
        logging.exception('play scan db upgrade')
        raise    
    logger.set_logger('play_scan_watch.log', to_sentry=True)
    seplis.play.scan_watch.main()

@cli.command()
def play_scan_cleanup():
    import seplis.play.scan
    try:
        seplis.play.scan.upgrade_scan_db()
    except:        
        logging.exception('play scan db upgrade')
        raise
    logger.set_logger('play_scan.log', to_sentry=True)
    seplis.play.scan.cleanup()

@cli.command()
def play_server():
    logger.set_logger('play_server.log', to_sentry=True)
    import seplis.play.app
    seplis.play.app.main()

def main():
    cli()

if __name__ == "__main__":
    main()