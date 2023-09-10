from fastapi import Depends
import sqlalchemy as sa
from datetime import date
from ...dependencies import get_current_user_no_raise, get_expand, get_session, AsyncSession
from ... import models, schemas
from .... import utils
from ...expand.episodes import expand_episodes
from .router import router


@router.get('/{series_id}/episodes', response_model=schemas.Page_cursor_result[schemas.Episode])
async def get_episodes(
    series_id: int,
    season: int | None = None,
    episode: int | None = None,
    number: int | None = None,
    air_date: date | None = None,
    air_date_ge: date | None = None,
    air_date_le: date | None = None,
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise),
    page_cursor: schemas.Page_cursor_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
    ).order_by(
        models.Episode.number
    )
    if season:
        query = query.where(models.Episode.season == season)
    if episode:
        query = query.where(models.Episode.episode == episode)
    if number:
        query = query.where(models.Episode.number == number)
    if air_date:
        query = query.where(models.Episode.air_date == air_date)
    if air_date_ge:
        query = query.where(models.Episode.air_date >= air_date_ge)
    if air_date_le:
        query = query.where(models.Episode.air_date <= air_date_le)

    p = await utils.sqlalchemy.paginate_cursor(
        session=session, 
        query=query,
        page_query=page_cursor,
    )
    p.items = [schemas.Episode.model_validate(row[0]) for row in p.items]
    await expand_episodes(episodes=p.items, series_id=series_id, user=user, expand=expand)
    return p