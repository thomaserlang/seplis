from fastapi import Depends, HTTPException, Security
import sqlalchemy as sa
from datetime import date
from ..dependencies import authenticated, get_current_user_no_raise, get_expand, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils
from ..expand.episodes import expand_episodes
from .series import router


@router.get('/{series_id}/episodes', response_model=schemas.Page_cursor_result[schemas.Episode])
async def get_episodes(
    series_id: int,
    season: int | None = None,
    episode: int | None = None,
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
    p.items = [schemas.Episode.from_orm(row[0]) for row in p.items]
    await expand_episodes(episodes=p.items, series_id=series_id, user=user, expand=expand, session=session)
    return p


@router.get('/{series_id}/episodes/{number}', response_model=schemas.Episode)
async def get_episode(
    series_id: int,
    number: int,
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Depends(get_current_user_no_raise),
    session: AsyncSession = Depends(get_session),
):
    episode = await session.scalar(sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
    if not episode:
        raise HTTPException(404, 'Unknown episode')
    
    episode = schemas.Episode.from_orm(episode)
    await expand_episodes(episodes=[episode], series_id=series_id, user=user, expand=expand, session=session)
    return episode


@router.delete('/{series_id}/episodes/{number}', status_code=204)
async def delete_episode(
    series_id: int,
    number: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_DELETE_SHOW)]),
):
    await session.execute(sa.delete(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
