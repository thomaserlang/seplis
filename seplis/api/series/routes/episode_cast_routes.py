from typing import Annotated

from fastapi import APIRouter, Depends, Security

from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.episode_cast_actions import (
    add_episode_cast,
    delete_episode_cast,
    get_episode_cast,
)
from ..schemas.episode_cast_schemas import EpisodeCastPerson, EpisodeCastPersonCreate

router = APIRouter()


@router.put(
    '/{series_id}/episodes/{episode_number}/cast',
    status_code=204,
    description="""
            **Scope required:** `series:edit`
            """,
)
async def episode_cast_add_route(
    series_id: int,
    episode_number: int,
    data: EpisodeCastPersonCreate,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> None:
    await add_episode_cast(series_id=series_id, episode_number=episode_number, data=data)


@router.delete(
    '/{series_id}/episodes/{episode_number}/cast/{person_id}',
    status_code=204,
    description="""
            **Scope required:** `series:edit`
            """,
)
async def episode_cast_delete_route(
    series_id: int,
    episode_number: int,
    person_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> None:
    await delete_episode_cast(
        series_id=series_id, episode_number=episode_number, person_id=person_id
    )


@router.get(
    '/{series_id}/episodes/{episode_number}/cast',
    description="""
            **Scope required:** `series:edit`
            """,
)
async def episode_cast_get_route(
    series_id: int,
    episode_number: int,
    page_query: Annotated[PageCursorQuery, Depends()],
) -> PageCursor[EpisodeCastPerson]:
    return await get_episode_cast(
        series_id=series_id,
        episode_number=episode_number,
        page_query=page_query,
    )
