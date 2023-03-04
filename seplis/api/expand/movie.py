import asyncio
import sqlalchemy as sa
from ..dependencies import AsyncSession
from .. import schemas, models, exceptions


async def expand_movies(expand: list[str], user: schemas.User_authenticated, movies: list[schemas.Movie], session: AsyncSession):
    if not expand:
        return
    if not user:
        raise exceptions.Not_signed_in_exception()
    expand_tasks = []
    if 'user_stared' in expand:
        expand_tasks.append(expand_user_stared(
            user_id=user.id,
            movies=movies,
            session=session
        ))
    if 'user_watched' in expand:
        expand_tasks.append(expand_user_watched(
            user_id=user.id,
            movies=movies,
            session=session
        ))
    if expand_tasks:
        await asyncio.gather(*expand_tasks)


async def expand_user_stared(user_id: int, movies: list[schemas.Movie], session: AsyncSession):
    _movies: dict[int, schemas.Movie] = {}
    for s in movies:
        s.user_stared = schemas.Movie_stared()
        _movies[s.id] = s
    result: list[models.Movie_stared] = await session.scalars(sa.select(
        models.Movie_stared,
    ).where(
        models.Movie_stared.user_id == user_id,
        models.Movie_stared.movie_id.in_(set(_movies.keys())),
    ))
    for s in result:
        _movies[s.movie_id].user_stared = \
            schemas.Movie_stared.from_orm(s)


async def expand_user_watched(user_id: int, movies: list[schemas.Movie], session: AsyncSession):
    _movies: dict[int, schemas.Movie] = {}
    for s in movies:
        s.user_watched = schemas.Movie_watched()
        _movies[s.id] = s
    result: list[models.Movie_watched] = await session.scalars(sa.select(
        models.Movie_watched,
    ).where(
        models.Movie_watched.user_id == user_id,
        models.Movie_watched.movie_id.in_(set(_movies.keys())),
    ))
    for s in result:
        _movies[s.movie_id].user_watched = \
            schemas.Movie_watched.from_orm(s)
