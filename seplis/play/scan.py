import os, os.path
import sqlalchemy as sa
from seplis import config, utils, logger
from seplis.play import models
from seplis.play.client import client
from seplis.play.database import database
from seplis.api import schemas

from .scanners import Movie_scan, Episode_scan


async def scan(disable_cleanup=False, disable_thumbnails=False):
    for s in config.data.play.scan:
        scanner = None
        if s.type == 'series':
            scanner = Episode_scan(
                scan_path=s.path, 
                make_thumbnails=s.make_thumbnails and not disable_thumbnails,
                cleanup_mode=not disable_cleanup,
            )
        elif s.type == 'movies':
            scanner = Movie_scan(
                scan_path=s.path, 
                make_thumbnails=s.make_thumbnails and not disable_thumbnails,
                cleanup_mode=not disable_cleanup,    
            )
        if scanner:
            await scanner.scan()
        else:
            logger.error(f'Scan type: "{s.type}" is not supported')

    if not disable_cleanup:
        await cleanup()


async def cleanup():
    logger.info('Cleanup started')
    await cleanup_episodes()
    await cleanup_movies()


async def cleanup_episodes():
    episodes: list[schemas.Play_server_episode_create] = []
    async with database.session() as session:
        deleted_count = 0
        rows = await session.stream(sa.select(models.Episode))
        async for db_episodes in rows.yield_per(500):
            for e in db_episodes:
                if os.path.exists(e.path):
                    episodes.append(schemas.Play_server_episode_create(
                        series_id=e.series_id,
                        episode_number=e.number,
                    ))
                    continue
                deleted_count += 1
                await session.execute(sa.delete(models.Episode).where(
                    models.Episode.series_id == e.series_id,
                    models.Episode.number == e.number,
                    models.Episode.path == e.path,
                ))
        await session.commit()
        logger.info(f'{deleted_count} episodes was deleted from the database')

        if not config.data.play.server_id:
            logger.warn(f'No server_id specified episodes not sent to play server index')
        else:
            r = await client.put(f'/2/play-servers/{config.data.play.server_id}/episodes', 
                data=utils.json_dumps(episodes),
                headers={
                    'Authorization': f'Secret {config.data.play.secret}',
                    'Content-Type': 'application/json',
                }
            )
            if r.status_code >= 400:
                logger.error(f'Faild to update the episode play server index ({config.data.play.server_id}): {r.content}')
            else:
                logger.info(f'Updated the episode play server index ({config.data.play.server_id})')


async def cleanup_movies():
    movies: list[schemas.Play_server_movie_create] = []
    async with database.session() as session:
        result = await session.stream(sa.select(models.Movie))
        deleted_count = 0
        async for db_movies in result.yield_per(500):
            for m in db_movies:
                if os.path.exists(m.path):
                    movies.append(schemas.Play_server_movie_create(
                        movie_id=m.movie_id,
                    ))
                    continue
                deleted_count += 1
                await session.execute(sa.delete(models.Movie).where(
                    models.Movie.movie_id == m.movie_id,
                    models.Movie.path == m.path,
                ))
        await session.commit()
        logger.info(f'{deleted_count} movies was deleted from the database')

        if not config.data.play.server_id:
            logger.warn(f'No server_id specified movies not sent to play server index')
        else:
            r = await client.put(f'/2/play-servers/{config.data.play.server_id}/movies', 
                data=utils.json_dumps(movies),
                headers={
                    'Authorization': f'Secret {config.data.play.secret}',
                    'Content-Type': 'application/json',
                }
            )
            if r.status_code >= 400:
                logger.error(f'Faild to update the movie play server index ({config.data.play.server_id}): {r.content}')
            else:
                logger.info(f'Updated the movie play server index ({config.data.play.server_id})')


def upgrade_scan_db():
    import alembic.config
    from alembic import command
    cfg = alembic.config.Config(
        os.path.dirname(
            os.path.abspath(__file__)
        )+'/alembic.ini'
    )
    cfg.set_main_option('script_location', 'seplis.play:migration')
    cfg.set_main_option('url', config.data.play.database)
    command.upgrade(cfg, 'head')