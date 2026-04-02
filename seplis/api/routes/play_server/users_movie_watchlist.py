from datetime import datetime
from typing import Literal

import sqlalchemy as sa
from fastapi import Depends
from pydantic import BaseModel

from seplis.api.filter.movies import filter_movies, filter_movies_query
from seplis.api.filter.movies.query_filter_schema import Movie_query_filter

from ... import models, schemas
from ...dependencies import AsyncSession, get_session
from .play_server import router


class Radarr_response(BaseModel):
    tmdbid: int
    id: int

@router.get('/{play_server_id}/users-movie-watchlist', 
            response_model=schemas.Page_cursor_result[schemas.Movie] | list[Radarr_response])
async def get_play_server_users_movie_watchlist(
    play_server_id: str,
    session: AsyncSession=Depends(get_session),
    page_query: schemas.Page_cursor_query = Depends(),
    filter_query: Movie_query_filter = Depends(),
    added_at_ge: datetime = None,
    added_at_le: datetime = None,
    response_format: Literal['standard', 'radarr'] = 'standard',
):
    query = sa.select(models.MMovie).where(
        models.MPlayServerAccess.play_server_id == play_server_id,
        models.MMovieWatchlist.user_id == models.MPlayServerAccess.user_id,
        models.MMovie.id == models.MMovieWatchlist.movie_id,
    ).order_by(models.MMovie.id).group_by(models.MMovie.id)

    if added_at_ge:
        query = query.where(
            models.MMovieWatchlist.created_at >= added_at_ge,
        )
    
    if added_at_le:
        query = query.where(
            models.MMovieWatchlist.created_at <= added_at_le,
        )

    if response_format == 'standard':
        return await filter_movies(
            query=query,
            session=session,
            filter_query=filter_query,
            page_cursor=page_query,
        )
    
    if response_format == 'radarr':
        query = filter_movies_query(query=query, filter_query=filter_query)
        rows = await session.scalars(query)
        return [Radarr_response(tmdbid=int(r.externals['themoviedb']), id=int(r.externals['themoviedb'])) 
                   for r in rows if r.externals.get('themoviedb')]
    return None
