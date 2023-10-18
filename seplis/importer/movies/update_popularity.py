import sqlalchemy as sa
from datetime import datetime

from seplis.api import exceptions
from ..themoviedb_export import get_ids
from . import importer
from ...api.database import database
from ...api import models, schemas
from ... import logger


async def update_popularity(create_movies = True, create_above_popularity: float | None = 1.0):
    logger.info('Updating movie popularity')
    movies: dict[str, schemas.Movie] = {}
    dt = datetime.now().date()
    async with database.session() as session:
        result = await session.stream(sa.select(models.Movie).options(sa.orm.noload("*")))
        async for db_movies in result.yield_per(1000):
            for movie in db_movies:
                if movie.externals.get('themoviedb'):
                    movies[movie.externals['themoviedb']] = movie.id

        ids_to_create = []
        insert_data = []
        async for data in get_ids('movie_ids'):
            id_ = str(data.id)
            if id_ in movies:
                insert_data.append({
                    'movie_id': movies[id_], 
                    'popularity': data.popularity or 0,
                    'date': dt,
                })
            elif create_movies and create_above_popularity != None and data.popularity >= create_above_popularity:
                ids_to_create.append(id_)
            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(models.Movie_popularity_history).prefix_with('IGNORE').values(insert_data),
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(models.Movie_popularity_history).prefix_with('IGNORE').values(insert_data),
            )
        await session.execute(sa.update(models.Movie).values({
                models.Movie.popularity: 0
            }),
        )
        await session.execute(sa.update(models.Movie).values({
                models.Movie.popularity: models.Movie_popularity_history.popularity
            }).where(
                models.Movie_popularity_history.date == dt,
                models.Movie_popularity_history.movie_id == models.Movie.id,
            ),
        )
        await session.commit()
        await models.rebuild_movies()

    for id_ in ids_to_create:
        try:
            logger.info(f'Creating movie TMDb id {id_}')
            movie_data = await importer.get_movie_data(id_)
            if not movie_data:
                continue
            movie = await models.Movie.save(
                data=movie_data,
            )
        except exceptions.Movie_external_duplicated as e:
            await models.Movie.save(data=schemas.Movie_update(
                externals={
                    'themoviedb': str(id_),
                },
            ), movie_id=e.extra['movie']['id'], patch=True)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            logger.error(str(e))