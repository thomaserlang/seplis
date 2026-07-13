from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import noload

from seplis.api import exceptions
from seplis.api.movie import (
    MMovie,
    MMoviePopularityHistory,
    MovieUpdate,
    rebuild_movies,
    save_movie,
)

from ... import logger
from ...api.database import database
from ..themoviedb_export import get_ids
from . import importer


async def update_popularity(
    create_movies: bool = True, create_above_popularity: float | None = 1.0
) -> None:
    logger.info('Updating movie popularity')
    movies: dict[str, int] = {}
    dt = datetime.now().date()
    async with database.session() as session:
        result = await session.stream(sa.select(MMovie).options(noload('*')))
        async for db_movies in result.yield_per(1000):
            for movie in db_movies:
                if movie.externals.get('themoviedb'):
                    movies[movie.externals['themoviedb']] = movie.id

        ids_to_create = []
        insert_data = []
        async for data in get_ids('movie_ids'):
            id_ = str(data.id)
            if id_ in movies:
                insert_data.append(
                    {
                        'movie_id': movies[id_],
                        'popularity': data.popularity or 0,
                        'date': dt,
                    }
                )
            elif (
                create_movies
                and create_above_popularity is not None
                and data.popularity >= create_above_popularity
            ):
                ids_to_create.append(id_)
            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(MMoviePopularityHistory.__table__)  # type: ignore
                    .prefix_with('IGNORE')
                    .values(insert_data),
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(MMoviePopularityHistory.__table__)  # type: ignore
                .prefix_with('IGNORE')
                .values(insert_data),
            )
        await session.execute(
            sa.update(MMovie.__table__).values({MMovie.popularity: 0}),  # type: ignore
        )
        await session.execute(
            sa.update(MMovie.__table__)  # type: ignore
            .values({MMovie.popularity: MMoviePopularityHistory.popularity})
            .where(
                MMoviePopularityHistory.date == dt,
                MMoviePopularityHistory.movie_id == MMovie.id,
            ),
        )
        await session.commit()
        await rebuild_movies()

    for id_ in ids_to_create:
        try:
            logger.info(f'Creating movie TMDb id {id_}')
            movie_data = await importer.get_movie_data(id_)
            if not movie_data:
                continue
            movie = await save_movie(
                data=movie_data,
            )
        except exceptions.MovieExternalDuplicated as e:
            await save_movie(
                data=MovieUpdate(
                    externals={
                        'themoviedb': str(id_),
                    },
                ),
                movie_id=e.extra['movie']['id'],
                patch=True,
            )
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception as e:
            logger.error(str(e))
