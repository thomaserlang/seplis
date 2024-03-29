from fastapi import Depends, Security
import sqlalchemy as sa
from datetime import datetime, timezone
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router


@router.get('/{series_id}/user-rating', response_model=schemas.Series_user_rating,
            description='''
            **Scope required:** `user:view_ratings`
            ''')
async def get_rating(
    series_id: int, 
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_ratings']),
):
    rating = await session.scalar(sa.select(models.Series_user_rating.rating).where(
        models.Series_user_rating.user_id == user.id,
        models.Series_user_rating.series_id == series_id,
    ))
    return schemas.Series_user_rating(rating=rating)


@router.put('/{series_id}/user-rating', status_code=204,
            description='''
            **Scope required:** `user:manage_ratings`
            ''')
async def update_rating(
    series_id: int,
    data: schemas.Series_user_rating_update,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_ratings']),
):
    sql = sa.dialects.mysql.insert(models.Series_user_rating).values(
        user_id=user.id,
        series_id=series_id,
        rating=data.rating,
        updated_at=datetime.now(tz=timezone.utc),
    )
    sql = sql.on_duplicate_key_update(
        rating=sql.inserted.rating,
        updated_at=sql.inserted.updated_at,
    )
    await session.execute(sql)


@router.delete('/{series_id}/user-rating', status_code=204,
            description='''
            **Scope required:** `user:manage_ratings`
            ''')
async def delete_rating(
    series_id: int,
    session: AsyncSession=Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:manage_ratings']),
):
    await session.execute(sa.delete(models.Series_user_rating).where(        
        models.Series_user_rating.user_id == user.id,
        models.Series_user_rating.series_id == series_id,
    ))