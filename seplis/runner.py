import click
import uvicorn
from seplis import config, logger, set_logger
from seplis.api import exceptions
import asyncio

async def run_task(*task):
    from seplis.api.database import database
    await database.setup()
    try:
        try:
            await asyncio.gather(*task)
        finally:
            await database.close()
    except exceptions.API_exception as e:
        logger.error(e.message)

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
    uvicorn.run('seplis.web.main:app', host='0.0.0.0', port=config.data.web.port, reload=config.data.debug, proxy_headers=True, forwarded_allow_ips='*')


@cli.command()
def api():
    uvicorn.run('seplis.api.main:app', host='0.0.0.0', port=config.data.api.port, reload=config.data.debug, proxy_headers=True, forwarded_allow_ips='*')


@cli.command()
def upgrade():
    set_logger('upgrade.log')
    import seplis.api.migrate
    seplis.api.migrate.upgrade()


@cli.command()
def rebuild_cache():
    set_logger('rebuild_cache.log')
    import seplis.api.rebuild_cache
    asyncio.run(run_task(seplis.api.rebuild_cache.rebuild()))


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
@click.option('--from_id', default=1, help='which series to start from')
@click.option('--do_async', is_flag=True, help='send the update task to the workers')
def update_movies_bulk(from_id, do_async):
    import seplis.importer
    set_logger('importer_update_movies_bulk.log')
    asyncio.run(run_task(seplis.importer.movies.update_movies_bulk(from_id, do_async=do_async)))


@cli.command()
@click.argument('person_id')
def update_person(person_id):
    import seplis.importer
    set_logger('importer_update_series_by_id.log')
    asyncio.run(run_task(seplis.importer.people.update_person_by_id(person_id)))


@cli.command()
@click.option('--create', is_flag=True, help='Enables creation of series/movies that we don\'t have')
@click.option('--create_above_popularity', default=None, help='create the series/movie if the specified popularity value is larger')
def update_popularity(create, create_above_popularity):
    import seplis.importer
    set_logger('importer_update_popularity.log')
    asyncio.run(run_task(
        seplis.importer.movies.update_popularity(
        create_movies=create or create_above_popularity,
        create_above_popularity=float(create_above_popularity) if create_above_popularity else 1.0,
        ),
        seplis.importer.series.update_popularity(
            create_series=create or create_above_popularity,
            create_above_popularity=float(create_above_popularity) if create_above_popularity else 1.0,
        )
    ))


@cli.command()
@click.option('--create', is_flag=True, help='Enables creation of movies that we don\'t have')
@click.option('--create_above_popularity', default=None, help='create the movie if the specified popularity value is larger')
def update_movies_popularity(create, create_above_popularity):
    import seplis.importer
    set_logger('importer_update_movies_popularity.log')
    asyncio.run(run_task(seplis.importer.movies.update_popularity(
        create_movies=create or create_above_popularity,
        create_above_popularity=float(create_above_popularity) if create_above_popularity else 1.0,
    )))


@cli.command()
@click.option('--create', is_flag=True, help='Enables creation of series that we don\'t have')
@click.option('--create_above_popularity', default=None, help='create the movie if the specified popularity value is larger')
def update_series_popularity(create, create_above_popularity):
    import seplis.importer
    set_logger('importer_update_series_popularity.log')
    asyncio.run(run_task(seplis.importer.series.update_popularity(
        create_series=create or create_above_popularity,
        create_above_popularity=float(create_above_popularity) if create_above_popularity else 1.0,
    )))


@cli.command()
def update_imdb_ratings():
    from seplis.importer.update_imdb_ratings import update_imdb_ratings
    set_logger('importer_update_series_popularity.log')
    asyncio.run(run_task(update_imdb_ratings()))


@cli.command()
def worker():
    import logging
    logging.basicConfig(level=config.data.logging.level.upper())
    import seplis.tasks.worker
    set_logger(f'worker.log')
    seplis.tasks.worker.main()


@cli.command()
def dev_server():
    set_logger('dev_server', to_sentry=False)
    import seplis.dev_server
    seplis.dev_server.main()


def main():
    cli()

if __name__ == "__main__":
    main()