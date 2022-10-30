from fastapi import APIRouter, Depends, Request, Security, Query
import sqlalchemy as sa
from typing import Literal

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/series-following')

@router.get('', response_model=schemas.Page_result[schemas.Series_with_user_rating])
async def get_series(
    request: Request,
    sort: Literal['followed_at', 'user_rating'] = 'followed_at',
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_query = Depends(),
):
    query = sa.select(models.Series, models.Series_user_rating.rating, models.Series_following.user_id).where(
        models.Series_following.show_id == models.Series.id,
        models.Series_following.user_id == user.id,
    ).join(
        models.Series_user_rating, sa.and_(
            models.Series_user_rating.show_id == models.Series_following.show_id,
            models.Series_user_rating.user_id == models.Series_following.user_id,
        ),
        isouter=True,
    )

    if sort == 'user_rating':
        query = query.order_by(
            sa.desc(models.Series_user_rating.rating),
            sa.desc(models.Series_following.created_at),
            sa.desc(models.Series_following.show_id),
        )
    else:
        query = query.order_by(
            sa.desc(models.Series_following.created_at),
            sa.desc(models.Series_following.show_id),
        )

    p = await utils.sqlalchemy.paginate(session=session, query=query, page_query=page_query, request=request, scalars=False)
    l: list[schemas.Series_with_user_rating] = []
    for item in p.items:
        o = schemas.Series_with_user_rating.from_orm(item.Series)
        o.user_rating = item.rating
        l.append(o)
    p.items = l
    return p