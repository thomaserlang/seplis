from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from seplis.api.contexts import get_session
from seplis.api.movie.actions.movie_mapping import select_movies
from seplis.api.movie.models.movie_model import MMovie
from seplis.api.movie.models.movie_watchlist_model import MMovieWatchlist
from seplis.api.movie.types.movie_filter_types import MovieQueryFilter
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.series.actions.series_mapping import select_series
from seplis.api.series.models.series_model import MSeries
from seplis.api.series.models.series_watchlist_model import MSeriesWatchlist
from seplis.api.series.types.series_filter_types import SeriesQueryFilter

from ..models.play_server_model import MPlayServerAccess
from ..schemas.play_server_schemas import RadarrResponse, SonarrResponse


async def get_play_server_users_movie_watchlist(
    play_server_id: str,
    page_query: PageCursorQuery,
    filter_query: MovieQueryFilter,
    added_at_ge: datetime | None,
    added_at_le: datetime | None,
    response_format: Literal['standard', 'radarr'],
    session: AsyncSession | None = None,
) -> PageCursor | list[RadarrResponse]:
    # Deferred because the movie filters import the play-server package.
    from seplis.api.movie.actions.movie_filter_actions import (
        filter_movies,
        filter_movies_query,
    )

    async with get_session(session) as session:
        query = (
            select_movies()
            .where(
                MPlayServerAccess.play_server_id == play_server_id,
                MMovieWatchlist.user_id == MPlayServerAccess.user_id,
                MMovie.id == MMovieWatchlist.movie_id,
            )
            .order_by(MMovie.id)
            .group_by(MMovie.id)
        )

        if added_at_ge:
            query = query.where(MMovieWatchlist.created_at >= added_at_ge)

        if added_at_le:
            query = query.where(MMovieWatchlist.created_at <= added_at_le)

        if response_format == 'standard':
            return await filter_movies(
                query=query,
                session=session,
                filter_query=filter_query,
                page_query=page_query,
            )

        query = filter_movies_query(query=query, filter_query=filter_query)
        rows = (await session.execute(query)).mappings()
        return [
            RadarrResponse(
                tmdbid=int(row['externals']['themoviedb']),
                id=int(row['externals']['themoviedb']),
            )
            for row in rows
            if row['externals'].get('themoviedb')
        ]


async def get_play_server_users_series_watchlist(
    play_server_id: str,
    page_query: PageCursorQuery,
    filter_query: SeriesQueryFilter,
    added_at_ge: datetime | None,
    added_at_le: datetime | None,
    response_format: Literal['standard', 'sonarr'],
    session: AsyncSession | None = None,
) -> PageCursor | list[SonarrResponse]:
    # Deferred because the series filters import the play-server package.
    from seplis.api.series.actions.series_filter_actions import (
        filter_series,
        filter_series_query,
    )

    async with get_session(session) as session:
        query = (
            select_series()
            .where(
                MPlayServerAccess.play_server_id == play_server_id,
                MSeriesWatchlist.user_id == MPlayServerAccess.user_id,
                MSeries.id == MSeriesWatchlist.series_id,
            )
            .group_by(MSeries.id)
        )

        if added_at_ge:
            query = query.where(MSeriesWatchlist.created_at >= added_at_ge)

        if added_at_le:
            query = query.where(MSeriesWatchlist.created_at <= added_at_le)

        if response_format == 'standard':
            return await filter_series(
                query=query,
                session=session,
                filter_query=filter_query,
                page_query=page_query,
            )

        query = filter_series_query(query=query, filter_query=filter_query)
        rows = (await session.execute(query)).mappings()
        return [
            SonarrResponse(TvdbId=int(row['externals']['thetvdb']))
            for row in rows
            if row['externals'].get('thetvdb')
        ]
