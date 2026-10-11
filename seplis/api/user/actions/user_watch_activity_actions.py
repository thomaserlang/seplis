from datetime import UTC, datetime

import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.movie.models.movie_model import MMovie, MMovieWatchedHistory
from seplis.api.series.models.episode_model import MEpisode, MEpisodeWatchedHistory
from seplis.api.series.models.series_model import MSeries

from ..schemas.user_watch_activity_schemas import UserWatchActivityMonth


async def get_user_watch_activity(
    user_id: int, session: AsyncSession | None = None
) -> list[UserWatchActivityMonth]:
    now = datetime.now(UTC)
    current_month = now.year * 12 + now.month - 1
    months = [
        UserWatchActivityMonth(month=f'{index // 12:04d}-{index % 12 + 1:02d}')
        for index in range(current_month - 11, current_month + 1)
    ]
    start = datetime.fromisoformat(f'{months[0].month}-01').replace(tzinfo=UTC)
    by_month = {item.month: item for item in months}
    async with get_session(session) as session:
        episode_year = sa.extract('year', MEpisodeWatchedHistory.watched_at)
        episode_month = sa.extract('month', MEpisodeWatchedHistory.watched_at)
        episode_rows = (
            await session.execute(
                sa.select(
                    episode_year.label('year'),
                    episode_month.label('month'),
                    sa.func.count().label('watched'),
                    sa.func.sum(
                        sa.func.coalesce(MEpisode.runtime, MSeries.runtime, 0)
                    ).label('minutes'),
                )
                .select_from(MEpisodeWatchedHistory.__table__)
                .join(
                    MEpisode.__table__,
                    sa.and_(
                        MEpisode.series_id == MEpisodeWatchedHistory.series_id,
                        MEpisode.number == MEpisodeWatchedHistory.episode_number,
                    ),
                )
                .join(MSeries.__table__, MSeries.id == MEpisode.series_id)
                .where(
                    MEpisodeWatchedHistory.user_id == user_id,
                    MEpisodeWatchedHistory.watched_at >= start,
                    MEpisodeWatchedHistory.watched_at <= now,
                )
                .group_by(episode_year, episode_month)
            )
        ).mappings()
        for row in episode_rows:
            item = by_month[f'{int(row["year"]):04d}-{int(row["month"]):02d}']
            item.episodes_watched = int(row['watched'])
            item.series_minutes = int(row['minutes'] or 0)

        movie_year = sa.extract('year', MMovieWatchedHistory.watched_at)
        movie_month = sa.extract('month', MMovieWatchedHistory.watched_at)
        movie_rows = (
            await session.execute(
                sa.select(
                    movie_year.label('year'),
                    movie_month.label('month'),
                    sa.func.count().label('watched'),
                    sa.func.sum(sa.func.coalesce(MMovie.runtime, 0)).label('minutes'),
                )
                .select_from(MMovieWatchedHistory.__table__)
                .join(MMovie.__table__, MMovie.id == MMovieWatchedHistory.movie_id)
                .where(
                    MMovieWatchedHistory.user_id == user_id,
                    MMovieWatchedHistory.watched_at >= start,
                    MMovieWatchedHistory.watched_at <= now,
                )
                .group_by(movie_year, movie_month)
            )
        ).mappings()
        for row in movie_rows:
            item = by_month[f'{int(row["year"]):04d}-{int(row["month"]):02d}']
            item.movies_watched = int(row['watched'])
            item.movie_minutes = int(row['minutes'] or 0)
    return months
