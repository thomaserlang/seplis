from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router


@router.get('/{series_id}/user-settings', response_model=schemas.User_series_settings,
            description='''
            **Scope required:** `user:progress`
            ''')
async def get_series_user_settings(
    series_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:progress']),
):
    settings = await session.scalar(sa.select(models.User_series_settings).where(
        models.User_series_settings.user_id == user.id,
        models.User_series_settings.series_id == series_id,
    ))
    if not settings:
        return schemas.User_series_settings()
    else:
        return settings


@router.put('/{series_id}/user-settings', response_model=schemas.User_series_settings,
            description='''
            **Scope required:** `user:manage_play_settings`
            ''')
async def set_series_user_settings(
    series_id: int,
    data: schemas.User_series_settings_update,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_play_settings']),
):
    settings = await session.scalar(sa.select(models.User_series_settings).where(
        models.User_series_settings.user_id == user.id,
        models.User_series_settings.series_id == series_id,
    ))
    if not settings:
        await session.execute(sa.insert(models.User_series_settings).values(
            series_id=series_id,
            user_id=user.id,
            **data.model_dump(exclude_unset=True)
        ))
    else:
        await session.execute(sa.update(models.User_series_settings).values(
            **data.model_dump(exclude_unset=True)
        ).where(
            models.User_series_settings.user_id == user.id,
            models.User_series_settings.series_id == series_id,
        ))
    settings = await session.scalar(sa.select(models.User_series_settings).where(
        models.User_series_settings.user_id == user.id,
        models.User_series_settings.series_id == series_id,
    ))
    await session.commit()
    return settings