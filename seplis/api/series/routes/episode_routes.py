from typing import Annotated

from fastapi import APIRouter, Depends, Security

from ...dependencies import (
    authenticated,
    get_current_user_no_raise,
    get_expand,
)
from ...user import UserAuthenticated
from ..actions.episode_actions import delete_episode, get_episode
from ..schemas.episode_schemas import Episode

router = APIRouter()


@router.get('/{series_id}/episodes/{number}')
async def get_episode_route(
    series_id: int,
    number: int,
    expand: Annotated[list[str] | None, Depends(get_expand)],
    user: Annotated[UserAuthenticated | None, Depends(get_current_user_no_raise)],
) -> Episode:
    return await get_episode(series_id=series_id, number=number, expand=expand, user=user)


@router.delete(
    '/{series_id}/episodes/{number}',
    status_code=204,
    description="""
            **Scope required:** `series:edit`
            """,
)
async def delete_episode_route(
    series_id: int,
    number: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['series:edit'])],
) -> None:
    await delete_episode(series_id=series_id, number=number)
