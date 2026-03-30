import asyncio
import signal
from collections.abc import Coroutine
from pathlib import Path
from types import FrameType
from typing import Any

import click
import uvicorn
from loguru import logger

from seplis import config
from seplis.api import exceptions
from seplis.logger_utils import set_logger


async def run_task(*task: Coroutine[Any, Any, Any]) -> None:
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
@click.option(
    '--log_path', '-lp', default=None, help='a folder to store the log files in'
)
@click.option(
    '--log_level',
    '-ll',
    default=None,
    help='notset, debug, info, warning, error or critical',
)
def cli(log_path: str | None, log_level: str | None) -> None:
    if log_path is not None:
        config.logging.path = Path(log_path)
    if log_level:
        config.logging.level = log_level  # type: ignore[assignment]


@cli.command()
def web() -> None:
    uvicorn.run(
        'seplis.web.main:app',
        host='0.0.0.0',
        port=config.web.port,
        reload=config.debug,
        proxy_headers=True,
        forwarded_allow_ips='*',
    )


@cli.command()
def api() -> None:
    uvicorn.run(
        'seplis.api.main:app',
        host='0.0.0.0',
        port=config.api.port,
        reload=config.debug,
        proxy_headers=True,
        forwarded_allow_ips='*',
    )


@cli.command()
@click.option('--revision', '-r', help='revision, default head', default='head')
@click.option('--keep-running', is_flag=True, help='Keep the process running forever')
def upgrade(revision: str, keep_running: bool) -> None:
    from alembic import command
    from alembic.config import Config

    cfg = Config(Path(__file__).parent / 'api/alembic.ini')
    cfg.set_main_option('script_location', 'seplis:api/migration')
    cfg.set_main_option('sqlalchemy.url', config.api.database)
    command.upgrade(cfg, revision)

    if keep_running:
        logger.info('Running forever...')
        with asyncio.Runner() as runner:
            runner.run(wait_for_shutdown(delay_secs=0))


shutdown_event = asyncio.Event()


def signal_handler(signum: int, frame: FrameType | None) -> None:
    if not shutdown_event.is_set():
        logger.info(f'Received signal {signum}, shutting down...')
    shutdown_event.set()


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


async def wait_for_shutdown(delay_secs: int = 1) -> None:
    while not shutdown_event.is_set():
        await asyncio.sleep(0.1)
    if delay_secs:
        await asyncio.sleep(delay_secs)


@cli.command()
def rebuild_cache() -> None:
    set_logger('rebuild_cache.log')
    import seplis.api.rebuild_cache

    asyncio.run(run_task(seplis.api.rebuild_cache.rebuild()))


@cli.command()
def update_series_incremental() -> None:
    import seplis.importer

    set_logger('importer_update_series.log')
    asyncio.run(run_task(seplis.importer.series.update_series_incremental()))


@cli.command()
@click.argument('series_id')
def update_series(series_id: str) -> None:
    import seplis.importer

    set_logger('importer_update_series_by_id.log')
    asyncio.run(run_task(seplis.importer.series.update_series_by_id(series_id)))


@cli.command()
@click.option('--from_id', default=1, help='which show to start from')
@click.option('--do_async', is_flag=True, help='send the update task to the workers')
def update_series_bulk(from_id: int, do_async: bool) -> None:
    import seplis.importer

    set_logger('importer_update_series_bulk.log')
    asyncio.run(
        run_task(seplis.importer.series.update_series_bulk(from_id, do_async=do_async))
    )


@cli.command()
@click.argument('movie_id')
def update_movie(movie_id: str) -> None:
    import seplis.importer

    set_logger('importer_update_movie.log')
    asyncio.run(run_task(seplis.importer.movies.update_movie(movie_id=movie_id)))


@cli.command()
def update_movies_incremental() -> None:
    import seplis.importer

    set_logger('importer_update_movies_incremental.log')
    asyncio.run(run_task(seplis.importer.movies.update_incremental()))


@cli.command()
@click.option('--from_id', default=1, help='which series to start from')
@click.option('--do_async', is_flag=True, help='send the update task to the workers')
def update_movies_bulk(from_id: int, do_async: bool) -> None:
    import seplis.importer

    set_logger('importer_update_movies_bulk.log')
    asyncio.run(
        run_task(seplis.importer.movies.update_movies_bulk(from_id, do_async=do_async))
    )


@cli.command()
@click.argument('person_id')
def update_person(person_id: str) -> None:
    import seplis.importer

    set_logger('importer_update_series_by_id.log')
    asyncio.run(run_task(seplis.importer.people.update_person_by_id(person_id)))


@cli.command()
@click.option(
    '--create', is_flag=True, help="Enables creation of series/movies that we don't have"
)
@click.option(
    '--create_above_popularity',
    default=None,
    help='create the series/movie if the specified popularity value is larger',
)
def update_popularity(create: bool, create_above_popularity: str | None) -> None:
    import seplis.importer

    set_logger('importer_update_popularity.log')
    asyncio.run(
        run_task(
            seplis.importer.movies.update_popularity(
                create_movies=create or bool(create_above_popularity),
                create_above_popularity=float(create_above_popularity)
                if create_above_popularity
                else 1.0,
            ),
            seplis.importer.series.update_popularity(
                create_series=create or bool(create_above_popularity),
                create_above_popularity=float(create_above_popularity)
                if create_above_popularity
                else 1.0,
            ),
        )
    )


@cli.command()
@click.option(
    '--create', is_flag=True, help="Enables creation of movies that we don't have"
)
@click.option(
    '--create_above_popularity',
    default=None,
    help='create the movie if the specified popularity value is larger',
)
def update_movies_popularity(create: bool, create_above_popularity: str | None) -> None:
    import seplis.importer

    set_logger('importer_update_movies_popularity.log')
    asyncio.run(
        run_task(
            seplis.importer.movies.update_popularity(
                create_movies=create or bool(create_above_popularity),
                create_above_popularity=float(create_above_popularity)
                if create_above_popularity
                else 1.0,
            )
        )
    )


@cli.command()
@click.option(
    '--create', is_flag=True, help="Enables creation of series that we don't have"
)
@click.option(
    '--create_above_popularity',
    default=None,
    help='create the movie if the specified popularity value is larger',
)
def update_series_popularity(create: bool, create_above_popularity: str | None) -> None:
    import seplis.importer

    set_logger('importer_update_series_popularity.log')
    asyncio.run(
        run_task(
            seplis.importer.series.update_popularity(
                create_series=create or bool(create_above_popularity),
                create_above_popularity=float(create_above_popularity)
                if create_above_popularity
                else 1.0,
            )
        )
    )


@cli.command()
def update_imdb_ratings() -> None:
    from seplis.importer.update_imdb_ratings import update_imdb_ratings

    set_logger('importer_update_series_popularity.log')
    asyncio.run(run_task(update_imdb_ratings()))


@cli.command()
def worker() -> None:
    import asyncio
    import logging

    logging.basicConfig(level=config.logging.level.upper())
    import seplis.tasks.worker

    asyncio.set_event_loop(asyncio.new_event_loop())
    set_logger('worker.log')
    seplis.tasks.worker.main()


@cli.command()
def dev_server() -> None:
    set_logger('dev_server', to_sentry=False)
    import seplis.dev_server

    seplis.dev_server.main()


def main() -> None:
    cli()


if __name__ == '__main__':
    main()
