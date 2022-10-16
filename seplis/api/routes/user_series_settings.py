from fastapi import Depends, Security, APIRouter
import sqlalchemy as sa

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants, exceptions

router = APIRouter(prefix='/2/series/{series_id}/user-settings')


@router.get('', response_model=schemas.User_series_settings)
async def get_user_series_settings(
    series_id: int,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_PROGRESS)]),
):
    settings = await session.scalar(sa.select(models.User_series_settings).where(
        models.User_series_settings.user_id == user.id,
        models.User_series_settings.show_id == series_id,
    ))
    if not settings:
        return schemas.User_series_settings()
    else:
        return settings


@router.put('', response_model=schemas.User_series_settings)
async def set_user_series_settings(
    series_id: int,
    data: schemas.User_series_settings_update,
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    settings = await session.scalar(sa.select(models.User_series_settings).where(
        models.User_series_settings.user_id == user.id,
        models.User_series_settings.show_id == series_id,
    ))
    if not settings:
        await session.execute(sa.insert(models.User_series_settings).values(
            show_id=series_id,
            user_id=user.id,
            **data.dict()
        ))
    else:
        await session.execute(sa.update(models.User_series_settings).values(
            **data.dict()
        ).where(
            models.User_series_settings.user_id == user.id,
            models.User_series_settings.show_id == series_id,
        ))
    settings = await session.scalar(sa.select(models.User_series_settings).where(
        models.User_series_settings.user_id == user.id,
        models.User_series_settings.show_id == series_id,
    ))
    await session.commit()
    return settings