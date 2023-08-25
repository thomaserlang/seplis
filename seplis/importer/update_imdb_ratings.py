import sqlalchemy as sa
import httpx
import tempfile
import os
import gzip
import csv
from aiofile import async_open
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from ..api.database import database
from ..api import models
from .. import logger


async def update_imdb_ratings():
    logger.info('Downloading imdb ratings')
    ratings = await get_ratings()
    dt = datetime.now().date()
    insert_data = []
    async with database.session() as session:
        logger.info('Updating imdb ratings for movies')
        result = await session.execute(sa.select(models.Movie.id, models.Movie.externals, models.Movie.rating, models.Movie.rating_votes))
        for movie in result:
            if movie.externals.get('imdb') not in ratings:
                continue
            if (ratings[movie.externals['imdb']].rating == movie.rating) and \
                (ratings[movie.externals['imdb']].votes == movie.rating_votes):
                continue
            insert_data.append({
                'movie_id': movie.id,
                'date': dt,
                'rating': ratings[movie.externals['imdb']].rating,
                'votes': ratings[movie.externals['imdb']].votes,
            })
            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(models.Movie_rating_history.__table__).prefix_with('IGNORE').values(insert_data),
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(models.Movie_rating_history.__table__).prefix_with('IGNORE').values(insert_data),
            )
        insert_data = []
        await session.execute(sa.update(models.Movie.__table__).values({
                models.Movie.rating: models.Movie_rating_history.rating,
                models.Movie.rating_votes: models.Movie_rating_history.votes,
            }).where(
                models.Movie_rating_history.date == dt,
                models.Movie_rating_history.movie_id == models.Movie.id,
            ),
        )
        await session.commit()
        await models.rebuild_movies()

    async with database.session() as session:
        logger.info('Updating imdb ratings for series')
        result = await session.execute(sa.select(models.Series.id, models.Series.externals, models.Series.rating, models.Series.rating_votes))
        for s in result:
            if s.externals.get('imdb') not in ratings:
                continue
            if (ratings[s.externals['imdb']].rating == s.rating) and \
                (ratings[s.externals['imdb']].votes == s.rating_votes):
                continue
            insert_data.append({
                'series_id': s.id,
                'date': dt,
                'rating': ratings[s.externals['imdb']].rating,
                'votes': ratings[s.externals['imdb']].votes,
            })

            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(models.Series_rating_history.__table__).prefix_with('IGNORE').values(insert_data),
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(models.Series_rating_history.__table__).prefix_with('IGNORE').values(insert_data),
            )
        insert_data = []
        await session.execute(sa.update(models.Series.__table__).values({
                models.Series.rating: models.Series_rating_history.rating,
                models.Series.rating_votes: models.Series_rating_history.votes,
            }).where(
                models.Series_rating_history.date == dt,
                models.Series_rating_history.series_id == models.Series.id,
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