import asyncio

import sqlalchemy as sa
from fastapi import Security

from seplis.api.user import UserSeriesStats

from ... import models
from ...database import auto_session
from ...dependencies import AsyncSession, authenticated
from .router import router


@router.get(
    '/user-stats',
    response_model=UserSeriesStats,
    description="""
            **Scope required:** `user:view_stats`
            """,
)
async def get_series(
    user: User_authenticated = Security(authenticated, scopes=['user:view_stats']),
):
    result = await asyncio.gather(
        series_watchlist(user.id),
        series_watched(user.id),
        episodes_watched(user.id),
        series_finished(user.id),
    )
    data: dict[str, int] = {}
    for r in result:
        data.update(r)
    return data


@auto_session
async def series_watchlist(
    user_id: int | str, session: AsyncSession = None
) -> dict[str, int]:
    count: int = await session.scalar(
        sa.select(sa.func.count(models.MSeriesWatchlist.series_id)).where(
            models.MSeriesWatchlist.user_id == user_id
        )
    )
    return {'series_watchlist': count}


@auto_session
async def series_watched(
    user_id: int | str, session: AsyncSession = None
) -> dict[str, int]:
    count: int = await session.scalar(
        sa.select(sa.func.count(models.MEpisodeLastWatched.series_id)).where(
            models.MEpisodeLastWatched.user_id == user_id,
        )
    )
    return {'series_watched': count}


@auto_session
async def episodes_watched(
    user_id: int | str, session: AsyncSession = None
) -> dict[str, int]:
    r = await session.execute(
        sa.select(
            sa.func.sum(models.MEpisodeWatched.times).label('episodes_watched'),
            sa.func.sum(
                models.MEpisodeWatched.times
                * sa.func.ifnull(
                    models.MEpisode.runtime,
                    sa.func.ifnull(models.MSeries.runtime, 0),
                )
            ).label('episodes_watched_minutes'),
        ).where(
            models.MEpisodeWatched.user_id == user_id,
            models.MEpisode.series_id == models.MEpisodeWatched.series_id,
            models.MEpisode.number == models.MEpisodeWatched.episode_number,
            models.MSeries.id == models.MEpisodeWatched.series_id,
        )
    )
    r = r.first()
    return {
        'episodes_watched': r.episodes_watched or 0,
        'episodes_watched_minutes': r.episodes_watched_minutes or 0,
    }


@auto_session
async def series_finished(
    user_id: int | str, session: AsyncSession = None
) -> dict[str, int]:
    count: int = await session.scalar(
        sa.select(sa.func.count(models.MSeries.id)).where(
            models.MEpisodeWatched.user_id == user_id,
            models.MSeries.id == models.MEpisodeWatched.series_id,
            models.MEpisodeWatched.episode_number == models.MSeries.total_episodes,
            models.MEpisodeWatched.times > 0,
        )
    )
    return {'series_finished': count}
