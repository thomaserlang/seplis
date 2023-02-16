from fastapi import APIRouter, Depends
import sqlalchemy as sa
from ..dependencies import get_session, AsyncSession
from .. import models, schemas

router = APIRouter(prefix='/2/genres')

@router.get('', response_model=list[schemas.Genre])
async def get_series(
    session: AsyncSession=Depends(get_session),
):
    rows = await session.scalars(sa.select(models.Genre).order_by(models.Genre.name))
    return [schemas.Genre.from_orm(row) for row in rows]