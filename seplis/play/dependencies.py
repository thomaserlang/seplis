from sqlalchemy import select
from tornado import web
from fastapi import HTTPException
from seplis.play import database, models
from seplis import utils, config

async def get_metadata(play_id) -> list[dict]:
    data = decode_play_id(play_id)
    if data['type'] == 'series':
        query = select(models.Episode.meta_data).where(
            models.Episode.series_id == data['series_id'],
            models.Episode.number == data['number'],
        )
    elif data['type'] == 'movie':
        query = select(models.Movie.meta_data).where(
            models.Movie.movie_id == data['movie_id'],
        )
    async with database.session() as session:
        return await session.scalars(query)

def decode_play_id(play_id: str) -> list[dict]:
    data = web.decode_signed_value(
        secret=config.data.play.secret,
        name='play_id',
        value=play_id,
        max_age_days=0.3,
    )
    if not data:
        raise HTTPException(400, 'Play id invalid')
    return utils.json_loads(data)