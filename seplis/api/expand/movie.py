import asyncio
import sqlalchemy as sa
from ..database import auto_session
from ..dependencies import AsyncSession
from .. import schemas, models, exceptions


async def expand_movies(expand: list[str], user: schemas.User_authenticated, movies: list[schemas.Movie]):
    if not expand:
        return
    if not user:
        raise exceptions.Not_signed_in_exception()
    expand_tasks = []
    if 'user_watchlist' in expand:
        expand_tasks.append(expand_user_watchlist(
            user_id=user.id,
            movies=movies,
        ))
    if 'user_favorite' in expand:
        expand_tasks.append(expand_user_favorite(
            user_id=user.id,
            movies=movies,
        ))
    if 'user_watched' in expand:
        expand_tasks.append(expand_user_watched(
            user_id=user.id,
            movies=movies,
        ))
    if expand_tasks:
        await asyncio.gather(*expand_tasks)


@auto_session
async def expand_user_watchlist(user_id: int, movies: list[schemas.Movie], session: AsyncSession):
    _movies: dict[int, schemas.Movie] = {}
    for s in movies:
        s.user_watchlist = schemas.Movie_watchlist()
        _movies[s.id] = s
    result: list[models.Movie_watchlist] = await session.scalars(sa.select(
        models.Movie_watchlist,
    ).where(
        models.Movie_watchlist.user_id == user_id,
        models.Movie_watchlist.movie_id.in_(set(_movies.keys())),
    ))
    for s in result:
        _movies[s.movie_id].user_watchlist = schemas.Movie_watchlist.model_validate(s)
        _movies[s.movie_id].user_watchlist.on_watchlist = True


@auto_session
async def expand_user_favorite(user_id: int, movies: list[schemas.Movie], session: AsyncSession):
    _movies: dict[int, schemas.Movie] = {}
    for s in movies:
        s.user_favorite = schemas.Movie_favorite()
        _movies[s.id] = s
    result: list[models.Movie_favorite] = await session.scalars(sa.select(
        models.Movie_favorite,
    ).where(
        models.Movie_favorite.user_id == user_id,
        models.Movie_favorite.movie_id.in_(set(_movies.keys())),
    ))
    for s in result:
        _movies[s.movie_id].user_favorite = schemas.Movie_favorite.model_validate(s)
        _movies[s.movie_id].user_favorite.favorite = True
        

@auto_session
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
            schemas.Movie_watched.model_validate(s)
