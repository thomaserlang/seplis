import click, signal, sys
import uvicorn
from seplis import config, logger, set_logger
import asyncio

async def run_task(task):
    from seplis.api.database import database
    await database.setup()
    try:
        await task
    finally:
        await database.close()

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
def web():
    uvicorn.run('seplis.web.main:app', host='0.0.0.0', port=config.data.web.port, reload=config.data.debug)

@cli.command()
def api():
    uvicorn.run('seplis.api.main:app', host='0.0.0.0', port=config.data.api.port, reload=config.data.debug)

@cli.command()
def play_server():
    uvicorn.run('seplis.play.main:app', host='0.0.0.0', port=config.data.play.port, reload=config.data.debug)

@cli.command()
def upgrade():
    set_logger('upgrade.log')
    import seplis.api.migrate
    seplis.api.migrate.upgrade()
    
@cli.command()
def rebuild_cache():
    set_logger('rebuild_cache.log')
    from seplis.api.connections import database
    database.connect()
    import seplis.api.rebuild_cache
    seplis.api.rebuild_cache.main()


@cli.command()
def update_series_incremental():
    import seplis.importer
    set_logger('importer_update_series.log')    
    asyncio.run(run_task(seplis.importer.series.update_series_incremental()))


@cli.command()
@click.argument('series_id')
def update_series(series_id):
    import seplis.importer
    set_logger('importer_update_series_by_id.log')
    asyncio.run(run_task(seplis.importer.series.update_series_by_id(series_id)))


@cli.command()
@click.option('--from_id', default=1, help='which show to start from')
@click.option('--do_async', is_flag=True, help='send the update task to the workers')
def update_series_bulk(from_id, do_async):
    import seplis.importer    
    set_logger('importer_update_series_bulk.log')
    asyncio.run(run_task(seplis.importer.series.update_series_bulk(from_id, do_async=do_async)))


@cli.command()
@click.argument('movie_id')
def update_movie(movie_id):
    import seplis.importer
    set_logger('importer_update_movie.log')
    asyncio.run(run_task(seplis.importer.movies.update_movie(movie_id=movie_id)))


@cli.command()
def update_movies_incremental():
    import seplis.importer
    set_logger('importer_update_movies_incremental.log')
    asyncio.run(run_task(seplis.importer.movies.update_incremental()))


@cli.command()
@click.option('--from_id', default=1, help='which show to start from')
@click.option('--do_async', is_flag=True, help='send the update task to the workers')
def update_movies_bulk(from_id, do_async):
    import seplis.importer
    set_logger('importer_update_movies_bulk.log')
    asyncio.run(run_task(seplis.importer.movies.update_movies_bulk(from_id, do_async=do_async)))


@cli.command()
@click.option('-n', default=1, help='worker number')
def worker(n):
    set_logger(f'worker-{n}.log')
    import seplis.tasks.worker
    from seplis.api.connections import database
    database.connect()
    seplis.tasks.worker.main()

@cli.command()
@click.option('--disable-cleanup', is_flag=True, help='Disable cleanup after scan')
@click.option('--disable-thumbnails', is_flag=True, help='Disable making thumbnails')
def play_scan(disable_cleanup, disable_thumbnails):
    set_logger('play_scan.log')
    import seplis.play.scan
    from seplis.play.database import database
    database.connect()
    seplis.play.scan.upgrade_scan_db()
    r = seplis.play.scan.scan(disable_thumbnails=disable_thumbnails)
    if not disable_cleanup:
        seplis.play.scan.cleanup()

@cli.command()
def play_scan_watch():
    set_logger('play_scan_watch.log')
    import seplis.play.scan_watch
    import seplis.play.scan
    from seplis.play.database import database
    database.connect()
    seplis.play.scan.upgrade_scan_db()
    seplis.play.scan_watch.main()

@cli.command()
def play_scan_cleanup():
    set_logger('play_scan_cleanup.log')
    import seplis.play.scan
    from seplis.play.database import database
    database.connect()
    seplis.play.scan.upgrade_scan_db()
    seplis.play.scan.cleanup()
    
@cli.command()
def dev_server():
    set_logger('dev_server', to_sentry=False)
    import seplis.dev_server
    seplis.dev_server.main()

def main():
    cli()

if __name__ == "__main__":
    main()