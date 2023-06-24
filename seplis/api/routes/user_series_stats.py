from fastapi import APIRouter, Depends, Security
import sqlalchemy as sa
import asyncio

from ..database import auto_session
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants


router = APIRouter(prefix='/2/users/me/series-stats')

@router.get('', response_model=schemas.User_series_stats)
async def get_series(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    result = await asyncio.gather(
        series_watchlist(user.id),
        series_watched(user.id),
        episodes_watched(user.id),
        series_finished(user.id)
    )
    data: dict[str, int] = {}
    for r in result:
        data.update(r)
    return data


@auto_session
async def series_watchlist(user_id: int | str, session: AsyncSession = None) -> dict[str, int]:
    count: int = await session.scalar(sa.select(sa.func.count(models.Series_watchlist.series_id)).where(
        models.Series_watchlist.user_id == user_id
    ))
    return {'series_watchlist': count}


@auto_session
async def series_watched(user_id: int | str, session: AsyncSession = None) -> dict[str, int]:
    count: int = await session.scalar(sa.select(sa.func.count(models.Episode_last_watched.series_id)).where(
        models.Episode_last_watched.user_id == user_id,
    ))
    return {'series_watched': count}


@auto_session
async def episodes_watched(user_id: int | str, session: AsyncSession = None) -> dict[str, int]:
    r = await session.execute(sa.select(
        sa.func.sum(models.Episode_watched.times).label('episodes_watched'),
        sa.func.sum(
            models.Episode_watched.times * \
                sa.func.ifnull(
                    models.Episode.runtime,
                    sa.func.ifnull(models.Series.runtime, 0),
                )
        ).label('episodes_watched_minutes'),
    ).where(
        models.Episode_watched.user_id == user_id,
        models.Episode.series_id == models.Episode_watched.series_id,
        models.Episode.number == models.Episode_watched.episode_number,
        models.Series.id == models.Episode_watched.series_id,
    ))
    r = r.first()
    return {
        'episodes_watched': r.episodes_watched or 0,
        'episodes_watched_minutes': r.episodes_watched_minutes or 0,
    }


@auto_session
async def series_finished(user_id: int | str, session: AsyncSession = None) -> dict[str, int]:
    count: int = await session.scalar(sa.select(
        sa.func.count(models.Series.id)
    ).where(
        models.Episode_watched.user_id == user_id,
        models.Series.id == models.Episode_watched.series_id,
        models.Episode_watched.episode_number == models.Series.total_episodes,
        models.Episode_watched.times > 0,
    ))
    return {'series_finished': count}
