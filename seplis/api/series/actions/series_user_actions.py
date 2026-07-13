import asyncio
from datetime import UTC, datetime

import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.user import (
    UserSeriesSettings,
    UserSeriesSettingsUpdate,
    UserSeriesStats,
)
from seplis.api.user.models.user_series_settings_model import MUserSeriesSettings

from ..models.episode_model import MEpisode, MEpisodeLastWatched, MEpisodeWatched
from ..models.series_favorite_model import MSeriesFavorite
from ..models.series_model import MSeries
from ..models.series_user_rating_model import MSeriesUserRating
from ..models.series_watchlist_model import MSeriesWatchlist
from ..schemas.series_schemas import (
    SeriesFavorite,
    SeriesUserRating,
    SeriesUserRatingUpdate,
    SeriesUserStats,
    SeriesWatchlist,
)


async def get_series_favorite(
    series_id: int, user_id: int, session: AsyncSession | None = None
) -> SeriesFavorite:
    async with get_session(session) as session:
        created_at = await session.scalar(
            sa.select(MSeriesFavorite.created_at).where(
                MSeriesFavorite.series_id == series_id,
                MSeriesFavorite.user_id == user_id,
            )
        )
        if created_at:
            return SeriesFavorite(favorite=True, created_at=created_at)
        return SeriesFavorite()


async def add_series_favorite(
    series_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.insert(MSeriesFavorite.__table__)  # type: ignore
            .values(
                series_id=series_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
            .prefix_with('IGNORE')
        )


async def remove_series_favorite(
    series_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(MSeriesFavorite.__table__).where(  # type: ignore
                MSeriesFavorite.series_id == series_id,
                MSeriesFavorite.user_id == user_id,
            )
        )


async def get_series_watchlist(
    series_id: int, user_id: int, session: AsyncSession | None = None
) -> SeriesWatchlist:
    async with get_session(session) as session:
        created_at = await session.scalar(
            sa.select(MSeriesWatchlist.created_at).where(
                MSeriesWatchlist.series_id == series_id,
                MSeriesWatchlist.user_id == user_id,
            )
        )
        if created_at:
            return SeriesWatchlist(on_watchlist=True, created_at=created_at)
        return SeriesWatchlist()


async def add_series_watchlist(
    series_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.insert(MSeriesWatchlist.__table__)  # type: ignore
            .values(
                series_id=series_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
            .prefix_with('IGNORE')
        )


async def remove_series_watchlist(
    series_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(MSeriesWatchlist.__table__).where(  # type: ignore
                MSeriesWatchlist.series_id == series_id,
                MSeriesWatchlist.user_id == user_id,
            )
        )


async def get_series_rating(
    series_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> SeriesUserRating:
    async with get_session(session) as session:
        rating = await session.scalar(
            sa.select(MSeriesUserRating.rating).where(
                MSeriesUserRating.user_id == user_id,
                MSeriesUserRating.series_id == series_id,
            )
        )
        return SeriesUserRating(rating=rating)


async def update_series_rating(
    series_id: int,
    user_id: int,
    data: SeriesUserRatingUpdate,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        sql = sa.dialects.mysql.insert(MSeriesUserRating.__table__).values(  # type: ignore
            user_id=user_id,
            series_id=series_id,
            rating=data['rating'],
            updated_at=datetime.now(tz=UTC),
        )
        sql = sql.on_duplicate_key_update(
            rating=sql.inserted.rating,
            updated_at=sql.inserted.updated_at,
        )
        await session.execute(sql)


async def delete_series_rating(
    series_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(MSeriesUserRating.__table__).where(  # type: ignore
                MSeriesUserRating.user_id == user_id,
                MSeriesUserRating.series_id == series_id,
            )
        )


async def get_user_stats(
    series_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> SeriesUserStats:
    async with get_session(session) as session:
        result = await session.execute(
            sa.select(
                sa.func.ifnull(sa.func.sum(MEpisodeWatched.times), 0).label(
                    'episodes_watched'
                ),
                sa.func.ifnull(
                    sa.func.sum(
                        MEpisodeWatched.times
                        * sa.func.ifnull(
                            MEpisode.runtime,
                            sa.func.ifnull(MSeries.runtime, 0),
                        )
                    ),
                    0,
                ).label('episodes_watched_minutes'),
            ).where(
                MEpisodeWatched.user_id == user_id,
                MEpisodeWatched.series_id == series_id,
                MEpisode.series_id == MEpisodeWatched.series_id,
                MEpisode.number == MEpisodeWatched.episode_number,
                MSeries.id == MEpisodeWatched.series_id,
            )
        )
        row = result.first()
        if not row:
            return SeriesUserStats()
        return SeriesUserStats(
            episodes_watched=int(row.episodes_watched or 0),
            episodes_watched_minutes=int(row.episodes_watched_minutes or 0),
        )


async def get_all_user_stats(user_id: int) -> UserSeriesStats:
    result = await asyncio.gather(
        series_watchlist_count(user_id),
        series_watched_count(user_id),
        episodes_watched_count(user_id),
        series_finished_count(user_id),
    )
    data: dict[str, int] = {}
    for item in result:
        data.update(item)
    return UserSeriesStats(**data)


async def series_watchlist_count(
    user_id: int, session: AsyncSession | None = None
) -> dict[str, int]:
    async with get_session(session) as session:
        count = await session.scalar(
            sa.select(sa.func.count(MSeriesWatchlist.series_id)).where(
                MSeriesWatchlist.user_id == user_id
            )
        )
        return {'series_watchlist': int(count or 0)}


async def series_watched_count(
    user_id: int, session: AsyncSession | None = None
) -> dict[str, int]:
    async with get_session(session) as session:
        count = await session.scalar(
            sa.select(sa.func.count(MEpisodeLastWatched.series_id)).where(
                MEpisodeLastWatched.user_id == user_id,
            )
        )
        return {'series_watched': int(count or 0)}


async def episodes_watched_count(
    user_id: int, session: AsyncSession | None = None
) -> dict[str, int]:
    async with get_session(session) as session:
        result = await session.execute(
            sa.select(
                sa.func.sum(MEpisodeWatched.times).label('episodes_watched'),
                sa.func.sum(
                    MEpisodeWatched.times
                    * sa.func.ifnull(
                        MEpisode.runtime,
                        sa.func.ifnull(MSeries.runtime, 0),
                    )
                ).label('episodes_watched_minutes'),
            ).where(
                MEpisodeWatched.user_id == user_id,
                MEpisode.series_id == MEpisodeWatched.series_id,
                MEpisode.number == MEpisodeWatched.episode_number,
                MSeries.id == MEpisodeWatched.series_id,
            )
        )
        row = result.first()
        if not row:
            return {'episodes_watched': 0, 'episodes_watched_minutes': 0}
        return {
            'episodes_watched': int(row.episodes_watched or 0),
            'episodes_watched_minutes': int(row.episodes_watched_minutes or 0),
        }


async def series_finished_count(
    user_id: int, session: AsyncSession | None = None
) -> dict[str, int]:
    async with get_session(session) as session:
        count = await session.scalar(
            sa.select(sa.func.count(MSeries.id)).where(
                MEpisodeWatched.user_id == user_id,
                MSeries.id == MEpisodeWatched.series_id,
                MEpisodeWatched.episode_number == MSeries.total_episodes,
                MEpisodeWatched.times > 0,
            )
        )
        return {'series_finished': int(count or 0)}


def user_series_settings_mapper(
    settings: MUserSeriesSettings | None,
) -> UserSeriesSettings:
    if not settings:
        return UserSeriesSettings()
    return UserSeriesSettings(
        subtitle_lang=settings.subtitle_lang,
        audio_lang=settings.audio_lang,
    )


async def get_series_user_settings(
    series_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> UserSeriesSettings:
    async with get_session(session) as session:
        settings = await session.scalar(
            sa.select(MUserSeriesSettings).where(
                MUserSeriesSettings.user_id == user_id,
                MUserSeriesSettings.series_id == series_id,
            )
        )
        return user_series_settings_mapper(settings)


async def set_series_user_settings(
    series_id: int,
    user_id: int,
    data: UserSeriesSettingsUpdate,
    session: AsyncSession | None = None,
) -> UserSeriesSettings:
    async with get_session(session) as session:
        settings = await session.scalar(
            sa.select(MUserSeriesSettings).where(
                MUserSeriesSettings.user_id == user_id,
                MUserSeriesSettings.series_id == series_id,
            )
        )
        values = dict(data)
        if not settings:
            await session.execute(
                sa.insert(MUserSeriesSettings.__table__).values(  # type: ignore
                    series_id=series_id,
                    user_id=user_id,
                    **values,
                )
            )
        else:
            await session.execute(
                sa.update(MUserSeriesSettings.__table__)  # type: ignore
                .values(**values)
                .where(
                    MUserSeriesSettings.user_id == user_id,
                    MUserSeriesSettings.series_id == series_id,
                )
            )
        settings = await session.scalar(
            sa.select(MUserSeriesSettings).where(
                MUserSeriesSettings.user_id == user_id,
                MUserSeriesSettings.series_id == series_id,
            )
        )
        await session.commit()
        return user_series_settings_mapper(settings)
