from typing import Literal
from fastapi import APIRouter, Depends
import sqlalchemy as sa
from ..dependencies import get_session, AsyncSession
from .. import models, schemas

router = APIRouter(prefix='/2/genres')

@router.get('', response_model=list[schemas.Genre])
async def get_genres(
    type: Literal['series', 'movie'],
    session: AsyncSession=Depends(get_session),
):
    rows = await session.scalars(sa.select(models.Genre).where(
        models.Genre.type == type,
        models.Genre.number_of > 0,
    ).order_by(models.Genre.name))
    return [schemas.Genre.model_validate(row) for row in rows]