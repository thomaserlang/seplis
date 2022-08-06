import asyncio
import logging, click
import os
import signal
import sys
from seplis.logger import logger
from seplis import config

@click.group()
@click.option('--config', default=None, help='path to the config file')
@click.option('--log_path', '-lp', default=None, help='a folder to store the log files in')
@click.option('--log_level', '-ll', default=None, help='notset, debug, info, warning, error or critical')
def cli(config, log_path, log_level):
    import seplis
    seplis.config_load(config)
    if log_path != None:
        seplis.config.data.logging.path = log_path
    if log_level:
        seplis.config.data.logging.level = log_level

@cli.command()
@click.option('--port', '-p', help='the port')
def web(port):
    if port:
        config.data.web.port = port            
    import seplis.web.app
    seplis.web.app.main()

@cli.command()
@click.option('--port', '-p', help='the port')
def api(port):
    if port:
        config.data.api.port = port
    import seplis.api.app
    from seplis.api.connections import database
    database.connect()
    asyncio.run(seplis.api.app.main())

@cli.command()
@click.option('--port', '-p', help='the port')
def play_server(port):
    if port:
        config.data.play.port = port
    from seplis.play.connections import database
    database.connect()
    import seplis.play.app
    seplis.play.app.main()

@cli.command()
def upgrade():
    logger.set_logger('upgrade.log', to_sentry=True)
    import seplis.api.migrate
    seplis.api.migrate.upgrade()
    
@cli.command()
def rebuild_cache():
    logger.set_logger('rebuild_cache.log', to_sentry=True)
    from seplis.api.connections import database
    database.connect()
    import seplis.api.rebuild_cache
    try:
        seplis.api.rebuild_cache.main()
    except (KeyboardInterrupt, SystemExit):
        raise 
    except:
        logging.exception('rebuild_cache')

@cli.command()
def update_shows():
    import seplis.importer
    logger.set_logger('importer_update_shows.log', to_sentry=True)
    try:
        seplis.importer.shows.update_shows_incremental()
    except (KeyboardInterrupt, SystemExit):
        raise 
    except:
        logging.exception('importer_update_shows')

@cli.command()
@click.argument('show_id')
def update_show(show_id):
    import seplis.importer
    logger.set_logger('importer_update_show_by_id.log', to_sentry=True)
    try:
        seplis.importer.shows.update_show_by_id(show_id)
    except (KeyboardInterrupt, SystemExit):
        raise 
    except:
        logging.exception('update_show_by_id')

@cli.command()
@click.option('--from_id', default=1, help='which show to start from')
@click.option('--do_async', is_flag=True, help='send the update task to the workers')
def update_shows_all(from_id, do_async):
    import seplis.importer
    logger.set_logger('importer_update_shows_all.log', to_sentry=True)
    try:
        seplis.importer.shows.update_shows_all(from_id, do_async=do_async)
    except (KeyboardInterrupt, SystemExit):
        raise 
    except:
        logging.exception('update_shows_all')

@cli.command()
@click.argument('movie_id')
def update_movie(movie_id):
    import seplis.importer
    logger.set_logger('importer_update_movie.log', to_sentry=True)
    seplis.importer.movies.update_movie(movie_id)

@cli.command()
def update_movies():
    import seplis.importer
    logger.set_logger('importer_update_movies.log', to_sentry=True)
    seplis.importer.movies.update_incremental()

@cli.command()
@click.option('-n', default=1, help='worker number')
def worker(n):
    logger.set_logger(f'worker-{n}.log')
    import seplis.tasks.worker
    from seplis.api.connections import database
    database.connect()
    try:
        seplis.tasks.worker.main()
    except (KeyboardInterrupt, SystemExit):
        raise 
    except:
        logging.exception('worker')

@cli.command()
@click.option('--disable_cleanup', is_flag=True, help='Disable cleanup after scan')
def play_scan(disable_cleanup):
    logger.set_logger('play_scan.log', to_sentry=True)
    import seplis.play.scan
    from seplis.play.connections import database
    database.connect()
    seplis.play.scan.upgrade_scan_db()
    seplis.play.scan.scan()
    if not disable_cleanup:
        seplis.play.scan.cleanup()

@cli.command()
def play_scan_watch():
    logger.set_logger('play_scan_watch.log', to_sentry=True)
    import seplis.play.scan_watch
    import seplis.play.scan
    from seplis.play.connections import database
    database.connect()
    try:
        seplis.play.scan.upgrade_scan_db()
        seplis.play.scan_watch.main()
    except:
        logging.exception('play_scan_watch')

@cli.command()
def play_scan_cleanup():
    logger.set_logger('play_scan_cleanup.log', to_sentry=True)
    import seplis.play.scan
    from seplis.play.connections import database
    database.connect()
    try:
        seplis.play.scan.upgrade_scan_db()
        seplis.play.scan.cleanup()
    except:
        logging.exception('play_scan_cleanup')

@cli.command()
def dev_server():
    logger.set_logger('dev_server', to_sentry=False)
    import seplis.dev_server
    seplis.dev_server.main()

def main():
    signal.signal(signal.SIGINT, sigint_handler)
    cli()

def sigint_handler(signal, frame):
    sys.exit()

if __name__ == "__main__":
    main()