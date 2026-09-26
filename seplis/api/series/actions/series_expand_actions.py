import asyncio

import sqlalchemy as sa

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.play_server.models.play_server_model import (
    MPlayServerAccess,
    MPlayServerEpisode,
)
from seplis.api.user import UserAuthenticated

from ..models.episode_model import MEpisode, MEpisodeLastWatched
from ..models.series_favorite_model import MSeriesFavorite
from ..models.series_user_rating_model import MSeriesUserRating
from ..models.series_watchlist_model import MSeriesWatchlist
from ..schemas.episode_schemas import UserCanWatch
from ..schemas.series_schemas import (
    Series,
    SeriesFavorite,
    SeriesUserRating,
    SeriesWatchlist,
)
from .series_mapping import episode_row_mapper


async def expand_series(
    expand: list[str] | None, user: UserAuthenticated | None, series: list[Series]
) -> None:
    if not expand:
        return
    if not user:
        raise exceptions.NotSignedInException()
    expand_tasks = []
    if 'user_watchlist' in expand:
        expand_tasks.append(
            expand_user_watchlist(
                user_id=user.id,
                series=series,
            )
        )
    if 'user_favorite' in expand:
        expand_tasks.append(
            expand_user_favorite(
                user_id=user.id,
                series=series,
            )
        )
    if 'user_can_watch' in expand:
        expand_tasks.append(
            expand_user_can_watch(
                series=series,
                user_id=user.id,
            )
        )
    if 'user_last_episode_watched' in expand:
        expand_tasks.append(
            expand_user_last_episode_watched(
                series=series,
                user_id=user.id,
            )
        )
    if 'user_rating' in expand:
        expand_tasks.append(
            expand_user_rating(
                series=series,
                user_id=user.id,
            )
        )
    if expand_tasks:
        await asyncio.gather(*expand_tasks)


async def expand_user_watchlist(
    user_id: int, series: list[Series], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        series_by_id: dict[int, Series] = {}
        for series_item in series:
            series_item.user_watchlist = SeriesWatchlist()
            series_by_id[series_item.id] = series_item
        result = (
            await session.execute(
                sa.select(MSeriesWatchlist.__table__).where(
                    MSeriesWatchlist.user_id == user_id,
                    MSeriesWatchlist.series_id.in_(set(series_by_id.keys())),
                )
            )
        ).mappings()
        for series_watchlist in result:
            series_by_id[series_watchlist['series_id']].user_watchlist = SeriesWatchlist(
                created_at=series_watchlist['created_at'],
                on_watchlist=True,
            )


async def expand_user_favorite(
    user_id: int, series: list[Series], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        series_by_id: dict[int, Series] = {}
        for series_item in series:
            series_item.user_favorite = SeriesFavorite()
            series_by_id[series_item.id] = series_item
        result = (
            await session.execute(
                sa.select(MSeriesFavorite.__table__).where(
                    MSeriesFavorite.user_id == user_id,
                    MSeriesFavorite.series_id.in_(set(series_by_id.keys())),
                )
            )
        ).mappings()
        for series_favorite in result:
            series_by_id[series_favorite['series_id']].user_favorite = SeriesFavorite(
                created_at=series_favorite['created_at'],
                favorite=True,
            )


async def expand_user_can_watch(
    user_id: int, series: list[Series], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        series_by_id: dict[int, Series] = {}
        for series_item in series:
            series_item.user_can_watch = UserCanWatch()
            series_by_id[series_item.id] = series_item
        result = (
            await session.execute(
                sa.select(MPlayServerEpisode.__table__)
                .where(
                    MPlayServerAccess.user_id == user_id,
                    MPlayServerEpisode.play_server_id == MPlayServerAccess.play_server_id,
                    MPlayServerEpisode.series_id.in_(set(series_by_id.keys())),
                    MPlayServerEpisode.episode_number == 1,
                )
                .group_by(MPlayServerEpisode.series_id)
            )
        ).mappings()
        for series_play_server in result:
            series_by_id[series_play_server['series_id']].user_can_watch = UserCanWatch(
                on_play_server=True
            )


async def expand_user_last_episode_watched(
    user_id: int, series: list[Series], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        series_by_id: dict[int, Series] = {
            series_item.id: series_item for series_item in series
        }
        result = (
            await session.execute(
                sa.select(MEpisode.__table__).where(
                    MEpisodeLastWatched.user_id == user_id,
                    MEpisodeLastWatched.series_id.in_(set(series_by_id.keys())),
                    MEpisode.series_id == MEpisodeLastWatched.series_id,
                    MEpisode.number == MEpisodeLastWatched.episode_number,
                )
            )
        ).mappings()
        for episode in result:
            series_by_id[
                episode['series_id']
            ].user_last_episode_watched = episode_row_mapper(episode)


async def expand_user_rating(
    user_id: int, series: list[Series], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        series_by_id: dict[int, Series] = {}
        for series_item in series:
            series_item.user_rating = SeriesUserRating()
            series_by_id[series_item.id] = series_item
        result = (
            await session.execute(
                sa.select(MSeriesUserRating.__table__).where(
                    MSeriesUserRating.user_id == user_id,
                    MSeriesUserRating.series_id.in_(set(series_by_id.keys())),
                )
            )
        ).mappings()
        for series_rating in result:
            series_by_id[series_rating['series_id']].user_rating = SeriesUserRating(
                rating=series_rating['rating'],
                updated_at=series_rating['updated_at'],
            )
