from fastapi import Depends, HTTPException, Security, Request
import sqlalchemy as sa
from datetime import date
from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import logger, utils, config
from .series import router


@router.get('/{series_id}/episodes', response_model=schemas.Page_result[schemas.Episode])
async def get_episodes(
    series_id: int,
    request: Request,
    season: int | None = None,
    episode: int | None = None,
    air_date: date | None = None,
    page_query: schemas.Page_query = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
    )
    if season:
        query = query.where(models.Episode.season == season)
    if episode:
        query = query.where(models.Episode.episode == episode)
    if air_date:
        query = query.where(models.Episode.air_date == air_date)
    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request)
    p.items = [schemas.Episode.from_orm(episode) for episode in p.items]
    return p


@router.get('/{series_id}/episodes/{number}', response_model=schemas.Episode)
async def get_episode(
    series_id: int,
    number: int,
    session: AsyncSession = Depends(get_session),
):
    episode = await session.scalar(sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
    if not episode:
        raise HTTPException(404, 'Unknown episode')
    return schemas.Episode.from_orm(episode)


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