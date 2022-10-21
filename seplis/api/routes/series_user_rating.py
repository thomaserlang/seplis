from fastapi import APIRouter, Depends, Security
import sqlalchemy as sa
from datetime import datetime, timezone

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants


router = APIRouter(prefix='/2/series/{series_id}/user-rating')


@router.get('', response_model=schemas.Series_user_rating)
async def get_rating(
    series_id: int, 
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    rating = await session.scalar(sa.select(models.User_show_rating.rating).where(
        models.User_show_rating.user_id == user.id,
        models.User_show_rating.show_id == series_id,
    ))
    return schemas.Series_user_rating(rating=rating)


@router.put('', status_code=204)
async def update_rating(
    series_id: int,
    data: schemas.Series_user_rating_update,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    sql = sa.dialects.mysql.insert(models.User_show_rating).values(
        user_id=user.id,
        show_id=series_id,
        rating=data.rating,
        updated_at=datetime.now(tz=timezone.utc),
    )
    sql = sql.on_duplicate_key_update(
        rating=sql.inserted.rating,
        updated_at=sql.inserted.updated_at,
    )
    await session.execute(sql)


@router.delete('', status_code=204)
async def delete_rating(
    series_id: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
):
    await session.execute(sa.delete(models.User_show_rating).where(        
        models.User_show_rating.user_id == user.id,
        models.User_show_rating.show_id == series_id,
    ))