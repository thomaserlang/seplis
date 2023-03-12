import sqlalchemy as sa
import httpx
import tempfile
import os
import gzip
import csv
from aiofile import async_open
from pydantic import BaseModel

from ..api.database import database
from ..api import models, schemas
from .. import logger


async def update_imdb_ratings():
    logger.info('Downloading imdb ratings')
    ratings = await get_ratings()
    async with database.session() as session:
        logger.info('Updating imdb ratings for movies')
        result = await session.execute(sa.select(models.Movie.id, models.Movie.externals, models.Movie.rating, models.Movie.rating_votes))
        for movie in result:
            if movie.externals.get('imdb') not in ratings:
                continue
            if (ratings[movie.externals['imdb']].rating == movie.rating) and \
                (ratings[movie.externals['imdb']].votes == movie.rating_votes):
                continue
            await models.Movie.save(movie_id=movie.id, data=schemas.Movie_update(
                rating = ratings[movie.externals['imdb']].rating,
                rating_votes = ratings[movie.externals['imdb']].votes,
            ), session=session)

        logger.info('Updating imdb ratings for series')
        result = await session.execute(sa.select(models.Series.id, models.Series.externals, models.Series.rating, models.Series.rating_votes))
        for s in result:
            if s.externals.get('imdb') not in ratings:
                continue
            if (ratings[s.externals['imdb']].rating == s.rating) and \
                (ratings[s.externals['imdb']].votes == s.rating_votes):
                continue
            await models.Series.save(series_id=s.id, data=schemas.Series_update(
                rating = ratings[s.externals['imdb']].rating,
                rating_votes = ratings[s.externals['imdb']].votes,
            ), session=session)

        await session.commit()


class Rating(BaseModel, allow_population_by_field_name=True):
    rating: float
    votes: int


async def get_ratings():
    tmp = os.path.join(tempfile.mkdtemp('seplis'), 'data.gz')
    try:        
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', 'https://datasets.imdbws.com/title.ratings.tsv.gz') as r:
                async with async_open(tmp, 'wb') as f:
                    async for chunk in r.aiter_bytes():
                        await f.write(chunk)
            with gzip.open(tmp,mode='rt') as f:
                rows = csv.reader(f, delimiter="\t")
                next(rows)
                return {row[0]: Rating(rating=row[1], votes=row[2]) 
                    for row in rows}
    finally:
        os.remove(tmp)