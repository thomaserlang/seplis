import csv
import gzip
import os
import tempfile
from datetime import datetime

import httpx
import sqlalchemy as sa
from aiofile import async_open
from pydantic import BaseModel, ConfigDict

from .. import logger
from ..api import models
from ..api.database import database


async def update_imdb_ratings() -> None:
    logger.info('Downloading imdb ratings')
    ratings = await get_ratings()
    dt = datetime.now().date()
    insert_data = []
    async with database.session() as session:
        logger.info('Updating imdb ratings for movies')
        result = await session.execute(
            sa.select(
                models.MMovie.id,
                models.MMovie.externals,
                models.MMovie.rating,
                models.MMovie.rating_votes,
            )
        )
        for movie in result:
            if movie.externals.get('imdb') not in ratings:
                continue
            if (ratings[movie.externals['imdb']].rating == movie.rating) and (
                ratings[movie.externals['imdb']].votes == movie.rating_votes
            ):
                continue
            insert_data.append(
                {
                    'movie_id': movie.id,
                    'date': dt,
                    'rating': ratings[movie.externals['imdb']].rating,
                    'votes': ratings[movie.externals['imdb']].votes,
                }
            )
            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(models.MMovieRatingHistory.__table__)
                    .prefix_with('IGNORE')
                    .values(insert_data),
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(models.MMovieRatingHistory.__table__)
                .prefix_with('IGNORE')
                .values(insert_data),
            )
        insert_data = []
        await session.execute(
            sa.update(models.MMovie.__table__)
            .values(
                {
                    models.MMovie.rating: models.MMovieRatingHistory.rating,
                    models.MMovie.rating_votes: models.MMovieRatingHistory.votes,
                }
            )
            .where(
                models.MMovieRatingHistory.date == dt,
                models.MMovieRatingHistory.movie_id == models.MMovie.id,
            ),
        )
        await session.commit()
        await models.rebuild_movies()

    async with database.session() as session:
        logger.info('Updating imdb ratings for series')
        result = await session.execute(
            sa.select(
                models.MSeries.id,
                models.MSeries.externals,
                models.MSeries.rating,
                models.MSeries.rating_votes,
            )
        )
        for s in result:
            if s.externals.get('imdb') not in ratings:
                continue
            if (ratings[s.externals['imdb']].rating == s.rating) and (
                ratings[s.externals['imdb']].votes == s.rating_votes
            ):
                continue
            insert_data.append(
                {
                    'series_id': s.id,
                    'date': dt,
                    'rating': ratings[s.externals['imdb']].rating,
                    'votes': ratings[s.externals['imdb']].votes,
                }
            )

            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(models.MSeriesRatingHistory.__table__)
                    .prefix_with('IGNORE')
                    .values(insert_data),
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(models.MSeriesRatingHistory.__table__)
                .prefix_with('IGNORE')
                .values(insert_data),
            )
        insert_data = []
        await session.execute(
            sa.update(models.MSeries.__table__)
            .values(
                {
                    models.MSeries.rating: models.MSeriesRatingHistory.rating,
                    models.MSeries.rating_votes: models.MSeriesRatingHistory.votes,
                }
            )
            .where(
                models.MSeriesRatingHistory.date == dt,
                models.MSeriesRatingHistory.series_id == models.MSeries.id,
            ),
        )
        await session.commit()
        await models.rebuild_series()


class Rating(BaseModel):
    rating: float
    votes: int

    model_config = ConfigDict(from_attributes=True)


async def get_ratings():
    tmp = os.path.join(tempfile.mkdtemp('seplis'), 'data.gz')
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                'GET', 'https://datasets.imdbws.com/title.ratings.tsv.gz'
            ) as r:
                async with async_open(tmp, 'wb') as f:
                    async for chunk in r.aiter_bytes():
                        await f.write(chunk)
            with gzip.open(tmp, mode='rt') as f:
                rows = csv.reader(f, delimiter='\t')
                next(rows)
                return {row[0]: Rating(rating=row[1], votes=row[2]) for row in rows}
    finally:
        os.remove(tmp)
