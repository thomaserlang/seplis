from fastapi import APIRouter, Depends, Security, Query
import sqlalchemy as sa
from datetime import datetime, timezone, timedelta, date
from collections import OrderedDict

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import logger


router = APIRouter(prefix='/2/users/me/air-dates')


@router.get('', response_model=list[schemas.Series_air_dates])
async def get_air_dates(
    days_back: int = Query(default=2, ge=0, le=7),
    days_ahead: int = Query(default=7, ge=0, le=14),
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    now = datetime.now(tz=timezone.utc)
    rows = await session.execute(sa.select(models.Episode, models.Series).where(
        models.Series_following.user_id == user.id,
        models.Series_following.show_id == models.Series.id,
        models.Episode.show_id == models.Series.id,
        sa.func.date(models.Episode.air_datetime) >= (now - timedelta(days=days_back)).date(),
        sa.func.date(models.Episode.air_datetime) <= (now + timedelta(days=days_ahead)).date(),
    ).order_by(
        models.Episode.air_datetime, 
        models.Series.id,
    ))
    rows = rows.all()
    air_dates: dict[date, list[schemas.Series_with_episodes]] = OrderedDict()
    air_date_series: OrderedDict[int, schemas.Series_with_episodes] = OrderedDict()
    prev = None
    for r in rows:
        if prev == None:
            prev = r.Episode.air_datetime.date()
        if prev != r.Episode.air_datetime.date():
            air_dates[prev] = list(air_date_series.values())
            prev = r.Episode.air_datetime.date()
            air_date_series = OrderedDict()
        if r.Series.id not in air_date_series:
            air_date_series[r.Series.id] = schemas.Series_with_episodes.from_orm(r.Series)
        air_date_series[r.Series.id].episodes.append(schemas.Episode.from_orm(r.Episode))
    if rows:
        air_dates[prev] = list(air_date_series.values())
    return [schemas.Series_air_dates(air_date=d, series=air_dates[d]) for d in air_dates]