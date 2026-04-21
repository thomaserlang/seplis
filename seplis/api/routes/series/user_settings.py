import sqlalchemy as sa
from fastapi import Depends, Security

from seplis.api.user import UserSeriesSettings, UserSeriesSettingsUpdate
from seplis.api.user.models.user_series_settings_model import MUserSeriesSettings

from ...dependencies import AsyncSession, UserAuthenticated, authenticated, get_session
from .router import router


@router.get(
    '/{series_id}/user-settings',
    response_model=UserSeriesSettings,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def get_series_user_settings(
    series_id: int,
    session: AsyncSession = Depends(get_session),
    user: UserAuthenticated = Security(authenticated, scopes=['user:progress']),
):
    settings = await session.scalar(
        sa.select(MUserSeriesSettings).where(
            MUserSeriesSettings.user_id == user.id,
            MUserSeriesSettings.series_id == series_id,
        )
    )
    if not settings:
        return UserSeriesSettings()
    return settings


@router.put(
    '/{series_id}/user-settings',
    response_model=UserSeriesSettings,
    description="""
            **Scope required:** `user:manage_play_settings`
            """,
)
async def set_series_user_settings(
    series_id: int,
    data: UserSeriesSettingsUpdate,
    session: AsyncSession = Depends(get_session),
    user: UserAuthenticated = Security(
        authenticated, scopes=['user:manage_play_settings']
    ),
):
    settings = await session.scalar(
        sa.select(MUserSeriesSettings).where(
            MUserSeriesSettings.user_id == user.id,
            MUserSeriesSettings.series_id == series_id,
        )
    )
    if not settings:
        await session.execute(
            sa.insert(MUserSeriesSettings).values(
                series_id=series_id,
                user_id=user.id,
                **data.model_dump(exclude_unset=True),
            )
        )
    else:
        await session.execute(
            sa.update(MUserSeriesSettings)
            .values(**data.model_dump(exclude_unset=True))
            .where(
                MUserSeriesSettings.user_id == user.id,
                MUserSeriesSettings.series_id == series_id,
            )
        )
    settings = await session.scalar(
        sa.select(MUserSeriesSettings).where(
            MUserSeriesSettings.user_id == user.id,
            MUserSeriesSettings.series_id == series_id,
        )
    )
    await session.commit()
    return settings
