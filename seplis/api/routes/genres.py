from typing import Annotated, Literal

import sqlalchemy as sa
from fastapi import APIRouter, Depends

from .. import models, schemas
from ..dependencies import AsyncSession, get_session

router = APIRouter(prefix='/2/genres', tags=['Genres'])

@router.get('', response_model=list[schemas.Genre])
async def get_genres(
    type: Literal['series', 'movie'],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    rows = await session.scalars(sa.select(models.Genre).where(
        models.Genre.type == type,
        models.Genre.number_of > 0,
    ).order_by(models.Genre.name))
    return [schemas.Genre.model_validate(row) for row in rows]