from fastapi import APIRouter, Depends, Request, Security

from ..dependencies import authenticated, get_session, AsyncSession
from .. import models, schemas, constants
from ... import utils

router = APIRouter(prefix='/2/users/me/series-following')

@router.get('', response_model=schemas.Page_cursor_total_result[schemas.Series_user])
async def get_series_following(
    sort: schemas.SERIES_USER_SORT_TYPE = 'followed_at_desc',
    user: schemas.User_authenticated = Security(authenticated, scopes=[str(constants.LEVEL_USER)]),
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
):
    query = models.series_user_query(user_id=user.id, sort=sort)
    query = query.where(
        models.Series_follower.user_id == user.id,
        models.Series.id == models.Series_follower.series_id,
    )

    p = await utils.sqlalchemy.paginate_cursor_total(session=session, query=query, page_query=page_query)
    p.items = [models.series_user_result_parse(item) for item in p.items]
    return p