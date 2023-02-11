import asyncio
from fastapi import Depends, HTTPException, Security, Request
import sqlalchemy as sa
from datetime import date
from ..dependencies import authenticated, authenticated_if_expand, get_expand, get_session, AsyncSession
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
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Security(authenticated_if_expand, scopes=[str(constants.LEVEL_PROGRESS)]),
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
    if expand:
        expand_tasks = []
        if 'user_watched' in expand:
            expand_tasks.append(expand_user_watched(
                series_id=series_id, 
                user_id=user.id, 
                episodes=p.items, 
                session=session
            ))
        if 'user_can_watch' in expand:
            expand_tasks.append(expand_user_can_watch(
                series_id=series_id, 
                user_id=user.id, 
                episodes=p.items, 
                session=session
            ))
        await asyncio.gather(*expand_tasks)
    return p


@router.get('/{series_id}/episodes/{number}', response_model=schemas.Episode)
async def get_episode(
    series_id: int,
    number: int,
    expand: list[str] | None = Depends(get_expand),
    user: schemas.User_authenticated | None = Security(authenticated_if_expand, scopes=[str(constants.LEVEL_PROGRESS)]),
    session: AsyncSession = Depends(get_session),
):
    episode = await session.scalar(sa.select(models.Episode).where(
        models.Episode.series_id == series_id,
        models.Episode.number == number,
    ))
    if not episode:
        raise HTTPException(404, 'Unknown episode')
    
    episode = schemas.Episode.from_orm(episode)
    if expand:
        expand = [e.strip() for e in expand.split(',')]
        expand_tasks = []
        if 'user_watched' in expand:
            expand_tasks.append(expand_user_watched(
                series_id=series_id, 
                user_id=user.id, 
                episodes=[episode], 
                session=session
            ))
        if 'user_can_watch' in expand:
            expand_tasks.append(expand_user_can_watch(
                series_id=series_id, 
                user_id=user.id, 
                episodes=[episode], 
                session=session
            ))
        await asyncio.gather(*expand_tasks)
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


async def expand_user_watched(series_id: int, user_id: int, episodes: list[schemas.Episode], session: AsyncSession):
    _episodes: dict[int, schemas.Episode] = {}
    for episode in episodes:
        episode.user_watched = schemas.Episode_watched(episode_number=episode.number)
        _episodes[episode.number] = episode
    result: list[models.Episode_watched] = await session.scalars(sa.select(
        models.Episode_watched,
    ).where(
        models.Episode_watched.user_id == user_id,
        models.Episode_watched.series_id == series_id,
        models.Episode_watched.episode_number.in_(set(_episodes.keys())),
    ))
    for episode_watched in result:
        _episodes[episode_watched.episode_number].user_watched = \
            schemas.Episode_watched.from_orm(episode_watched)


async def expand_user_can_watch(series_id: int, user_id: int, episodes: list[schemas.Episode], session: AsyncSession):
    _episodes: dict[int, schemas.Episode] = {}
    for episode in episodes:
        episode.user_can_watch = schemas.User_can_watch()
        _episodes[episode.number] = episode
    result: list[models.Play_server_episode] = await session.scalars(sa.select(
        models.Play_server_episode,
    ).where(
        models.Play_server_episode.user_id == user_id,
        models.Play_server_episode.series_id == series_id,
        models.Play_server_episode.episode_number.in_(set(_episodes.keys())),
    ).group_by(models.Play_server_episode.episode_number))
    for episode_watched in result:
        _episodes[episode_watched.episode_number].user_can_watch.on_play_server = True
