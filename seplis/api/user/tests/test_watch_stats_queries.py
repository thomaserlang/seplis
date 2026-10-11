from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
import sqlalchemy as sa
from freezegun import freeze_time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from seplis.api.movie.actions.movie_stats_actions import get_user_movie_stats
from seplis.api.movie.models.movie_model import (
    MMovie,
    MMovieWatched,
    MMovieWatchedHistory,
)
from seplis.api.movie.models.movie_watchlist_model import MMovieWatchlist
from seplis.api.series.actions.series_mapping import total_runtime_minutes_column
from seplis.api.series.models.episode_model import (
    MEpisode,
    MEpisodeWatched,
    MEpisodeWatchedHistory,
)
from seplis.api.series.models.series_model import MSeries
from seplis.api.user.actions.user_watch_activity_actions import get_user_watch_activity


@pytest_asyncio.fixture
async def stats_session() -> AsyncGenerator[tuple[AsyncSession, dict[str, sa.Table]]]:
    metadata = sa.MetaData()
    tables = {}
    for model, columns in [
        (MMovie, ['id', 'runtime']),
        (MMovieWatched, ['movie_id', 'user_id', 'times']),
        (MMovieWatchlist, ['movie_id', 'user_id']),
        (MMovieWatchedHistory, ['movie_id', 'user_id', 'watched_at']),
        (MSeries, ['id', 'runtime']),
        (MEpisode, ['series_id', 'number', 'runtime', 'air_date', 'air_datetime']),
        (MEpisodeWatched, ['series_id', 'episode_number', 'user_id', 'times']),
        (
            MEpisodeWatchedHistory,
            ['series_id', 'episode_number', 'user_id', 'watched_at'],
        ),
    ]:
        tables[model.__tablename__] = sa.Table(
            model.__tablename__,
            metadata,
            *(sa.Column(name, model.__table__.c[name].type) for name in columns),
        )
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    try:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        async with AsyncSession(engine) as session:
            yield session, tables
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_movie_stats_counts_rewatches_and_isolates_users(
    stats_session: tuple[AsyncSession, dict[str, sa.Table]],
) -> None:
    session, tables = stats_session
    await session.execute(
        sa.insert(tables['movies']),
        [
            {'id': 1, 'runtime': 120},
            {'id': 2, 'runtime': None},
            {'id': 3, 'runtime': 90},
        ],
    )
    await session.execute(
        sa.insert(tables['movies_watched']),
        [
            {'movie_id': 1, 'user_id': 1, 'times': 2},
            {'movie_id': 2, 'user_id': 1, 'times': 1},
            {'movie_id': 3, 'user_id': 1, 'times': 0},
            {'movie_id': 3, 'user_id': 2, 'times': 4},
        ],
    )
    await session.execute(
        sa.insert(tables['movie_watchlist']),
        [
            {'movie_id': 3, 'user_id': 1},
            {'movie_id': 1, 'user_id': 2},
        ],
    )
    stats = await get_user_movie_stats(1, session)
    assert stats.movies_watched == 2
    assert stats.movie_watch_count == 3
    assert stats.total_watch_minutes == 240
    assert stats.movies_watchlist == 1
    empty = await get_user_movie_stats(3, session)
    assert empty.movies_watched == empty.movie_watch_count == 0
    assert empty.total_watch_minutes == empty.movies_watchlist == 0


@freeze_time('2026-01-15T12:00:00Z')
@pytest.mark.asyncio
async def test_series_length_counts_aired_runtime_once(
    stats_session: tuple[AsyncSession, dict[str, sa.Table]],
) -> None:
    session, tables = stats_session
    await session.execute(sa.insert(tables['series']), {'id': 1, 'runtime': 30})
    await session.execute(
        sa.insert(tables['episodes']),
        [
            {
                'series_id': 1,
                'number': number,
                'runtime': runtime,
                'air_date': datetime.fromisoformat(date).date() if date else None,
                'air_datetime': datetime.fromisoformat(stamp) if stamp else None,
            }
            for number, runtime, date, stamp in [
                (1, None, '2026-01-01', None),
                (2, 45, None, '2026-01-02T12:00:00Z'),
                (3, 100, '2026-02-01', None),
                (4, 100, '2026-01-15', '2026-01-15T15:00:00Z'),
                (5, 100, None, None),
            ]
        ],
    )
    query = (
        sa.select(total_runtime_minutes_column())
        .select_from(MSeries.__table__)
        .where(MSeries.id == 1)
    )
    assert await session.scalar(query) == 75
    await session.execute(
        sa.insert(tables['episodes_watched']),
        {'series_id': 1, 'episode_number': 1, 'user_id': 1, 'times': 3},
    )
    assert await session.scalar(query) == 75
    await session.execute(sa.delete(tables['episodes']))
    assert await session.scalar(query) == 0


@freeze_time('2026-01-15T12:00:00Z')
@pytest.mark.asyncio
async def test_monthly_activity_uses_history_and_utc_boundaries(
    stats_session: tuple[AsyncSession, dict[str, sa.Table]],
) -> None:
    session, tables = stats_session
    await session.execute(sa.insert(tables['movies']), {'id': 1, 'runtime': 120})
    await session.execute(sa.insert(tables['series']), {'id': 1, 'runtime': 30})
    await session.execute(
        sa.insert(tables['episodes']),
        [
            {'series_id': 1, 'number': 1, 'runtime': None},
            {'series_id': 1, 'number': 2, 'runtime': 45},
        ],
    )
    await session.execute(
        sa.insert(tables['episodes_watched_history']),
        [
            {
                'series_id': 1,
                'episode_number': number,
                'user_id': user,
                'watched_at': datetime.fromisoformat(stamp),
            }
            for number, user, stamp in [
                (1, 1, '2025-12-05T12:00:00Z'),
                (1, 1, '2025-12-06T12:00:00Z'),
                (2, 1, '2026-01-05T12:00:00Z'),
                (2, 2, '2026-01-05T12:00:00Z'),
                (2, 1, '2026-01-20T12:00:00Z'),
                (2, 1, '2025-01-31T12:00:00Z'),
            ]
        ],
    )
    await session.execute(
        sa.insert(tables['movies_watched_history']),
        [
            {
                'movie_id': 1,
                'user_id': 1,
                'watched_at': datetime.fromisoformat('2026-01-01T00:30:00+02:00'),
            },
            {'movie_id': 1, 'user_id': 1, 'watched_at': datetime(2026, 1, 2, tzinfo=UTC)},
        ],
    )
    months = await get_user_watch_activity(1, session, year=2025)
    assert len(months) == 12
    assert months[0].date == '2025-01-01'
    assert months[-1].date == '2025-12-01'
    assert months[0].episodes_watched == 1
    assert months[-1].episodes_watched == 2
    assert months[-1].series_minutes == 60
    assert months[-1].movies_watched == 1
    assert months[-1].movie_minutes == 120
    assert all(
        month.episodes_watched == month.movies_watched == 0 for month in months[1:-1]
    )
    days = await get_user_watch_activity(1, session, year=2026, month=1)
    assert len(days) == 31
    assert days[0].date == '2026-01-01'
    assert days[1].movie_minutes == 120
    assert days[4].series_minutes == 45
    assert sum(day.episodes_watched for day in days) == 1
    assert sum(day.movies_watched for day in days) == 1
    leap_days = await get_user_watch_activity(3, session, year=2024, month=2)
    assert len(leap_days) == 29
    assert leap_days[-1].date == '2024-02-29'
    empty = await get_user_watch_activity(3, session, year=2026)
    assert len(empty) == 12
    assert all(month.episodes_watched == month.movies_watched == 0 for month in empty)
