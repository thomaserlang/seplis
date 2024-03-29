import asyncio
import sqlalchemy as sa

from ..database import auto_session
from ..dependencies import AsyncSession
from .. import schemas, models, exceptions


async def expand_series(expand: list[str], user: schemas.User, series: list[schemas.Series]):
    if not expand:
        return
    if not user:
        raise exceptions.Not_signed_in_exception()
    expand_tasks = []
    if 'user_watchlist' in expand:
        expand_tasks.append(expand_user_watchlist(
            user_id=user.id, 
            series=series,
        ))
    if 'user_favorite' in expand:
        expand_tasks.append(expand_user_favorite(
            user_id=user.id, 
            series=series,
        ))
    if 'user_can_watch' in expand:
        expand_tasks.append(expand_user_can_watch(
            series=series, 
            user_id=user.id,
        ))
    if 'user_last_episode_watched' in expand:
        expand_tasks.append(expand_user_last_episode_watched(
            series=series, 
            user_id=user.id,
        ))
    if 'user_rating' in expand:
        expand_tasks.append(expand_user_rating(
            series=series, 
            user_id=user.id,
        ))
    if expand_tasks:
        await asyncio.gather(*expand_tasks)


@auto_session
async def expand_user_watchlist(user_id: int, series: list[schemas.Series], session: AsyncSession):
    _series: dict[int, schemas.Series] = {}
    for s in series:
        s.user_watchlist = schemas.Series_watchlist()
        _series[s.id] = s
    result: list[models.Series_watchlist] = await session.scalars(sa.select(
        models.Series_watchlist,
    ).where(
        models.Series_watchlist.user_id == user_id,
        models.Series_watchlist.series_id.in_(set(_series.keys())),
    ))
    for s in result:
        _series[s.series_id].user_watchlist = schemas.Series_watchlist.model_validate(s)
        _series[s.series_id].user_watchlist.on_watchlist = True


@auto_session
async def expand_user_favorite(user_id: int, series: list[schemas.Series], session: AsyncSession):
    _series: dict[int, schemas.Series] = {}
    for s in series:
        s.user_favorite = schemas.Series_favorite()
        _series[s.id] = s
    result: list[models.Series_favorite] = await session.scalars(sa.select(
        models.Series_favorite,
    ).where(
        models.Series_favorite.user_id == user_id,
        models.Series_favorite.series_id.in_(set(_series.keys())),
    ))
    for s in result:
        _series[s.series_id].user_favorite = schemas.Series_favorite.model_validate(s)
        _series[s.series_id].user_favorite.favorite = True
        

@auto_session
async def expand_user_can_watch(user_id: int, series: list[schemas.Episode], session: AsyncSession):
    _series: dict[int, schemas.Episode] = {}
    for s in series:
        s.user_can_watch = schemas.User_can_watch()
        _series[s.id] = s
    result: list[models.Play_server_episode] = await session.scalars(sa.select(
        models.Play_server_episode,
    ).where(
        models.Play_server_access.user_id == user_id,
        models.Play_server_episode.play_server_id == models.Play_server_access.play_server_id,
        models.Play_server_episode.series_id.in_(set(_series.keys())),
        models.Play_server_episode.episode_number == 1,
    ).group_by(models.Play_server_episode.series_id))
    for s in result:
        _series[s.id].user_can_watch.on_play_server = True


@auto_session
async def expand_user_last_episode_watched(user_id: int, series: list[schemas.Series], session: AsyncSession):
    _series: dict[int, schemas.Series] = {s.id: s for s in series}
    result: list[models.Episode] = await session.scalars(sa.select(
        models.Episode
    ).where(
        models.Episode_last_watched.user_id == user_id,
        models.Episode_last_watched.series_id.in_(set(_series.keys())),
        models.Episode.series_id == models.Episode_last_watched.series_id,
        models.Episode.number == models.Episode_last_watched.episode_number,
    ))
    for episode in result:
        _series[episode.series_id].user_last_episode_watched = \
            schemas.Episode.model_validate(episode)
    

@auto_session
async def expand_user_rating(user_id: int, series: list[schemas.Series], session: AsyncSession):
    _series: dict[int, schemas.Series] = {}
    for s in series:
        s.user_can_watch = schemas.Series_user_rating()
        _series[s.id] = s
    result: list[models.Series_user_rating] = await session.scalars(sa.select(
        models.Series_user_rating,
    ).where(
        models.Series_user_rating.user_id == user_id,
        models.Series_user_rating.series_id.in_(set(_series.keys())),
    ))
    for s in result:
        _series[s.series_id].user_rating = schemas.Series_user_rating.model_validate(s)