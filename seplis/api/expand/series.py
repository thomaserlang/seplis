import asyncio

import sqlalchemy as sa

from .. import exceptions, models, schemas
from ..database import auto_session
from ..dependencies import AsyncSession


async def expand_series(expand: list[str], user: schemas.User, series: list[schemas.Series]) -> None:
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
async def expand_user_watchlist(user_id: int, series: list[schemas.Series], session: AsyncSession) -> None:
    _series: dict[int, schemas.Series] = {}
    for s in series:
        s.user_watchlist = schemas.Series_watchlist()
        _series[s.id] = s
    result: list[models.MSeriesWatchlist] = await session.scalars(sa.select(
        models.MSeriesWatchlist,
    ).where(
        models.MSeriesWatchlist.user_id == user_id,
        models.MSeriesWatchlist.series_id.in_(set(_series.keys())),
    ))
    for s in result:
        _series[s.series_id].user_watchlist = schemas.Series_watchlist.model_validate(s)
        _series[s.series_id].user_watchlist.on_watchlist = True


@auto_session
async def expand_user_favorite(user_id: int, series: list[schemas.Series], session: AsyncSession) -> None:
    _series: dict[int, schemas.Series] = {}
    for s in series:
        s.user_favorite = schemas.Series_favorite()
        _series[s.id] = s
    result: list[models.MSeriesFavorite] = await session.scalars(sa.select(
        models.MSeriesFavorite,
    ).where(
        models.MSeriesFavorite.user_id == user_id,
        models.MSeriesFavorite.series_id.in_(set(_series.keys())),
    ))
    for s in result:
        _series[s.series_id].user_favorite = schemas.Series_favorite.model_validate(s)
        _series[s.series_id].user_favorite.favorite = True
        

@auto_session
async def expand_user_can_watch(user_id: int, series: list[schemas.Episode], session: AsyncSession) -> None:
    _series: dict[int, schemas.Episode] = {}
    for s in series:
        s.user_can_watch = schemas.User_can_watch()
        _series[s.id] = s
    result: list[models.MPlayServerEpisode] = await session.scalars(sa.select(
        models.MPlayServerEpisode,
    ).where(
        models.MPlayServerAccess.user_id == user_id,
        models.MPlayServerEpisode.play_server_id == models.MPlayServerAccess.play_server_id,
        models.MPlayServerEpisode.series_id.in_(set(_series.keys())),
        models.MPlayServerEpisode.episode_number == 1,
    ).group_by(models.MPlayServerEpisode.series_id))
    for s in result:
        _series[s.id].user_can_watch.on_play_server = True


@auto_session
async def expand_user_last_episode_watched(user_id: int, series: list[schemas.Series], session: AsyncSession) -> None:
    _series: dict[int, schemas.Series] = {s.id: s for s in series}
    result: list[models.MEpisode] = await session.scalars(sa.select(
        models.MEpisode
    ).where(
        models.MEpisodeLastWatched.user_id == user_id,
        models.MEpisodeLastWatched.series_id.in_(set(_series.keys())),
        models.MEpisode.series_id == models.MEpisodeLastWatched.series_id,
        models.MEpisode.number == models.MEpisodeLastWatched.episode_number,
    ))
    for episode in result:
        _series[episode.series_id].user_last_episode_watched = \
            schemas.Episode.model_validate(episode)
    

@auto_session
async def expand_user_rating(user_id: int, series: list[schemas.Series], session: AsyncSession) -> None:
    _series: dict[int, schemas.Series] = {}
    for s in series:
        s.user_can_watch = schemas.Series_user_rating()
        _series[s.id] = s
    result: list[models.MSeriesUserRating] = await session.scalars(sa.select(
        models.MSeriesUserRating,
    ).where(
        models.MSeriesUserRating.user_id == user_id,
        models.MSeriesUserRating.series_id.in_(set(_series.keys())),
    ))
    for s in result:
        _series[s.series_id].user_rating = schemas.Series_user_rating.model_validate(s)