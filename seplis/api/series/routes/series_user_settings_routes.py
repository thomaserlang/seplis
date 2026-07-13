from typing import Annotated

from fastapi import APIRouter, Security

from seplis.api.user import UserSeriesSettings, UserSeriesSettingsUpdate

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_user_actions import (
    get_series_user_settings,
    set_series_user_settings,
)

router = APIRouter()


@router.get(
    '/{series_id}/user-settings',
    description="""
            **Scope required:** `user:progress`
            """,
)
async def get_series_user_settings_route(
    series_id: int,
    user: Annotated[UserAuthenticated, Security(authenticated, scopes=['user:progress'])],
) -> UserSeriesSettings:
    return await get_series_user_settings(series_id=series_id, user_id=user.id)


@router.put(
    '/{series_id}/user-settings',
    description="""
            **Scope required:** `user:manage_play_settings`
            """,
)
async def set_series_user_settings_route(
    series_id: int,
    data: UserSeriesSettingsUpdate,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['user:manage_play_settings'])
    ],
) -> UserSeriesSettings:
    return await set_series_user_settings(series_id=series_id, user_id=user.id, data=data)
