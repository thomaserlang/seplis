from fastapi import APIRouter, Depends, Security
import sqlalchemy as sa
import asyncio

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/series-stats')

@router.get('', response_model=schemas.User_series_stats)
async def get_series(
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
):
    result = await asyncio.gather(
        series_following(session, user.id),
        series_watched(session, user.id),
        episodes_watched(session, user.id),
        series_finished(session, user.id)
    )
    data: dict[str, int] = {}
    for r in result:
        data.update(r)
    return data

async def series_following(session: AsyncSession, user_id: int | str) -> dict[str, int]:
    count: int = await session.scalar(sa.select(sa.func.count(models.Series_following.show_id)).where(
        models.Series_following.user_id == user_id
    ))
    return {'series_following': count}


async def series_watched(session: AsyncSession, user_id: int | str) -> dict[str, int]:
    count: int = await session.scalar(sa.select(sa.func.count(models.Episode_watching.show_id)).where(
        models.Episode_watching.user_id == user_id,
    ))
    return {'series_watched': count}


async def episodes_watched(session: AsyncSession, user_id: int | str) -> dict[str, int]:
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
        models.Episode.show_id == models.Episode_watched.show_id,
        models.Episode.number == models.Episode_watched.episode_number,
        models.Series.id == models.Episode_watched.show_id,
    ))
    r = r.first()
    return {
        'episodes_watched': r['episodes_watched'] or 0,
        'episodes_watched_minutes': r['episodes_watched_minutes'] or 0,
    }


async def series_finished(session: AsyncSession, user_id: int | str) -> dict[str, int]:
    count: int = await session.scalar(sa.select(
        sa.func.count(models.Series.id)
    ).where(
        models.Episode_watched.user_id == user_id,
        models.Series.id == models.Episode_watched.show_id,
        models.Episode_watched.episode_number == models.Series.total_episodes,
        models.Episode_watched.times > 0,
    ))
    return {'series_finished': count}
