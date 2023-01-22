import sqlalchemy as sa
from ..themoviedb_export import get_ids
from . import importer
from ...api.database import database
from ...api import models, schemas
from ... import logger


async def update_popularity(create_movies = True, create_above_popularity: float | None = 1.0):
    logger.info('Updating movie popularity')
    movies: dict[str, schemas.Movie] = {}
    async with database.session() as session:
        result = await session.stream(sa.select(models.Movie))
        async for db_movies in result.yield_per(500):
            for movie in db_movies:
                s = schemas.Movie.from_orm(movie)
                if s.externals.get('themoviedb'):
                    movies[s.externals['themoviedb']] = s

    async for data in get_ids('movie_ids'):
        try:
            id_ = str(data.id)
            if id_ in movies:
                if movies[id_].popularity == data.popularity:
                    continue
                logger.info(f'Updating movie: {movies[id_].id}, popularity: {data.popularity}')
                await models.Movie.save(movie_id=movies[id_].id, data=schemas.Movie_update(
                    popularity=data.popularity
                ))

            elif create_movies and create_above_popularity != None and data.popularity >= create_above_popularity:
                logger.info(f'Creating themoviedb id {id_}, popularity: {data.popularity}')
                movie = await models.Movie.save(data=schemas.Movie_create(
                    externals={
                        'themoviedb': id_,
                    },
                    popularity=data.popularity,    
                ))
                await importer.update_movie(movie=movie)
                
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception(f'update_popularity {data.id}')