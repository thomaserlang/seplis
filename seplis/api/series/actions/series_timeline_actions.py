from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor

from ..models.episode_model import MEpisode, MEpisodeWatched, episode_mapper
from ..models.series_model import MSeries, series_mapper
from ..models.series_watchlist_model import MSeriesWatchlist
from ..schemas.series_schemas import SeriesAndEpisode
from ..types.series_filter_types import SeriesQueryFilter
from .series_filter_actions import filter_series_query


def series_and_episode_mapper(row: RowMapping) -> SeriesAndEpisode:
    return SeriesAndEpisode(
        series=series_mapper(row['MSeries']),
        episode=episode_mapper(row['MEpisode']),
    )


async def get_series_recently_aired(
    page_query: PageCursorQuery,
    filter_query: SeriesQueryFilter,
    days_ahead: int,
    days_behind: int,
    session: AsyncSession | None = None,
) -> PageCursor[SeriesAndEpisode]:
    async with get_session(session) as session:
        now = datetime.now(tz=UTC)
        episodes_query = (
            sa.select(
                MEpisode.series_id,
                sa.func.min(MEpisode.number).label('episode_number'),
            )
            .where(
                MEpisode.air_datetime > (now - timedelta(days=days_behind)),
                MEpisode.air_datetime < (now + timedelta(days=days_ahead)),
                MSeries.id == MEpisode.series_id,
            )
            .group_by(MEpisode.series_id)
        )

        episodes_query = filter_series_query(
            query=episodes_query,
            filter_query=filter_query,
            can_watch_episode_number=MEpisode.number,
        )
        episodes_query = episodes_query.subquery()

        query = (
            sa.select(MSeries, MEpisode)
            .where(
                MSeries.id == episodes_query.c.series_id,
                MEpisode.series_id == MSeries.id,
                MEpisode.number == episodes_query.c.episode_number,
            )
            .order_by(
                sa.desc(sa.func.coalesce(MEpisode.air_datetime, '1970-01-01 00:00:00')),
                MEpisode.series_id,
            )
        )

        return await page_cursor(
            session=session,
            query=query,
            page_query=page_query,
            count_total=False,
            record_mapper=series_and_episode_mapper,
        )


async def get_series_countdown(
    user_id: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[SeriesAndEpisode]:
    async with get_session(session) as session:
        episodes_query = (
            sa.select(
                MEpisode.series_id,
                sa.func.min(MEpisode.number).label('episode_number'),
            )
            .where(
                MSeriesWatchlist.user_id == user_id,
                MEpisode.series_id == MSeriesWatchlist.series_id,
                MEpisode.air_datetime > datetime.now(tz=UTC),
            )
            .group_by(MEpisode.series_id)
            .subquery()
        )
        query = (
            sa.select(MSeries, MEpisode)
            .where(
                MSeries.id == episodes_query.c.series_id,
                MEpisode.series_id == MSeries.id,
                MEpisode.number == episodes_query.c.episode_number,
            )
            .order_by(
                sa.asc(sa.func.coalesce(MEpisode.air_datetime, '1970-01-01 00:00:00')),
                MEpisode.series_id,
            )
        )

        return await page_cursor(
            session=session,
            query=query,
            page_query=page_query,
            count_total=False,
            record_mapper=series_and_episode_mapper,
        )


async def get_user_series_to_watch(
    user_id: int,
    page_query: PageCursorQuery,
    filter_query: SeriesQueryFilter,
    session: AsyncSession | None = None,
) -> PageCursor[SeriesAndEpisode]:
    async with get_session(session) as session:
        episodes_query = (
            sa.select(
                MEpisodeWatched.series_id,
                sa.func.max(MEpisodeWatched.episode_number).label('episode_number'),
            )
            .where(
                MSeriesWatchlist.user_id == user_id,
                MEpisodeWatched.user_id == MSeriesWatchlist.user_id,
                MEpisodeWatched.series_id == MSeriesWatchlist.series_id,
                MEpisodeWatched.times > 0,
            )
            .group_by(MEpisodeWatched.series_id)
            .subquery()
        )

        latest_aired_episode = (
            sa.select(
                MEpisode.series_id,
                sa.func.max(MEpisode.air_datetime).label('latest_aired_episode_datetime'),
            )
            .where(
                MSeriesWatchlist.user_id == user_id,
                MEpisode.series_id == MSeriesWatchlist.series_id,
                MEpisode.air_datetime <= datetime.now(tz=UTC),
            )
            .group_by(MEpisode.series_id)
            .subquery()
        )

        query = sa.select(MSeries, MEpisode).where(
            MSeries.id == episodes_query.c.series_id,
            MEpisode.series_id == MSeries.id,
            MEpisode.number == episodes_query.c.episode_number + 1,
            MEpisode.air_datetime <= datetime.now(tz=UTC),
            latest_aired_episode.c.series_id == MSeries.id,
        )

        query = (
            filter_series_query(
                query=query,
                filter_query=filter_query,
                can_watch_episode_number=MEpisode.number,
            )
            .order_by(None)
            .order_by(
                sa.desc(latest_aired_episode.c.latest_aired_episode_datetime),
                sa.desc(sa.func.coalesce(MSeries.popularity, 0)),
                MEpisode.series_id,
            )
        )
        return await page_cursor(
            session=session,
            query=query,
            page_query=page_query,
            record_mapper=series_and_episode_mapper,
        )
