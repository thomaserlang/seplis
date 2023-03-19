from fastapi import Depends
from datetime import datetime
import sqlalchemy as sa
from ..dependencies import get_session, AsyncSession
from .. import models, schemas
from ... import utils
from .play_server import router


@router.get('/{play_server_id}/users-movie-watchlist', response_model=schemas.Page_cursor_result[schemas.Movie])
async def get_play_server_users_movie_watchlist(
    play_server_id: str,
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
    added_at_ge: datetime = None,
    added_at_le: datetime = None,
):
    query = sa.select(models.Movie).where(
        models.Play_server_access.play_server_id == play_server_id,
        models.Movie_watchlist.user_id == models.Play_server_access.user_id,
        models.Movie.id == models.Movie_watchlist.movie_id,
    ).order_by(models.Movie.id).group_by(models.Movie.id)

    if added_at_ge:
        query = query.where(
            models.Movie_watchlist.created_at >= added_at_ge,
        )
    
    if added_at_le:
        query = query.where(
            models.Movie_watchlist.created_at <= added_at_le,
        )

    p = await utils.sqlalchemy.paginate_cursor(session=session, query=query, page_query=page_query)
    p.items = [r.Movie for r in p.items]
    return p
