from datetime import UTC, datetime
from typing import cast

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session

from ..models.movie_favorite_model import MMovieFavorite
from ..models.movie_model import MMovieWatched, MMovieWatchedHistory
from ..models.movie_watchlist_model import MMovieWatchlist
from ..schemas.movie_schemas import (
    MovieFavorite,
    MovieWatched,
    MovieWatchedIncrement,
    MovieWatchlist,
)


def movie_watched_mapper(watched: RowMapping) -> MovieWatched:
    return MovieWatched(
        times=watched['times'] or 0,
        position=watched['position'] or 0,
        watched_at=watched['watched_at'],
    )


async def get_movie_favorite(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> MovieFavorite:
    async with get_session(session) as session:
        created_at = await session.scalar(
            sa.select(MMovieFavorite.created_at).where(
                MMovieFavorite.user_id == user_id,
                MMovieFavorite.movie_id == movie_id,
            )
        )
        if not created_at:
            return MovieFavorite()
        return MovieFavorite(favorite=True, created_at=created_at)


async def add_movie_favorite(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.insert(cast(sa.Table, MMovieFavorite.__table__))
            .values(
                movie_id=movie_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
            .prefix_with('IGNORE')
        )


async def remove_movie_favorite(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(cast(sa.Table, MMovieFavorite.__table__)).where(
                MMovieFavorite.movie_id == movie_id,
                MMovieFavorite.user_id == user_id,
            )
        )


async def get_movie_watchlist(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> MovieWatchlist:
    async with get_session(session) as session:
        created_at = await session.scalar(
            sa.select(MMovieWatchlist.created_at).where(
                MMovieWatchlist.user_id == user_id,
                MMovieWatchlist.movie_id == movie_id,
            )
        )
        if not created_at:
            return MovieWatchlist()
        return MovieWatchlist(on_watchlist=True, created_at=created_at)


async def add_movie_watchlist(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.insert(cast(sa.Table, MMovieWatchlist.__table__))
            .values(
                movie_id=movie_id,
                user_id=user_id,
                created_at=datetime.now(tz=UTC),
            )
            .prefix_with('IGNORE')
        )


async def remove_movie_watchlist(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(cast(sa.Table, MMovieWatchlist.__table__)).where(
                MMovieWatchlist.movie_id == movie_id,
                MMovieWatchlist.user_id == user_id,
            )
        )


async def get_movie_watched(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> MovieWatched:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(MMovieWatched.__table__).where(
                        MMovieWatched.user_id == user_id,
                        MMovieWatched.movie_id == movie_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        return movie_watched_mapper(watched) if watched else MovieWatched()


async def increment_movie_watched(
    *,
    movie_id: int,
    user_id: int,
    data: MovieWatchedIncrement,
    session: AsyncSession | None = None,
) -> MovieWatched:
    async with get_session(session) as session:
        watched_at = data.get('watched_at') or datetime.now(tz=UTC)
        watched_stmt = mysql_insert(cast(sa.Table, MMovieWatched.__table__)).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=watched_at.astimezone(UTC),
            times=1,
        )
        watched_stmt = watched_stmt.on_duplicate_key_update(
            watched_at=watched_stmt.inserted.watched_at,
            times=MMovieWatched.times + 1,
            position=0,
        )
        watched_history_stmt = sa.insert(
            cast(sa.Table, MMovieWatchedHistory.__table__)
        ).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=watched_at.astimezone(UTC),
        )

        await session.execute(watched_stmt)
        await session.execute(watched_history_stmt)
        await session.execute(
            sa.delete(cast(sa.Table, MMovieWatchlist.__table__)).where(
                MMovieWatchlist.user_id == user_id,
                MMovieWatchlist.movie_id == movie_id,
            )
        )
        watched = (
            (
                await session.execute(
                    sa.select(MMovieWatched.__table__).where(
                        MMovieWatched.movie_id == movie_id,
                        MMovieWatched.user_id == user_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        return movie_watched_mapper(watched) if watched else MovieWatched()


async def decrement_movie_watched(
    *,
    movie_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> MovieWatched:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(MMovieWatched.__table__).where(
                        MMovieWatched.movie_id == movie_id,
                        MMovieWatched.user_id == user_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        if not watched:
            return MovieWatched()

        if watched['times'] == 0 or (watched['times'] == 1 and watched['position'] == 0):
            await session.execute(
                sa.delete(cast(sa.Table, MMovieWatched.__table__)).where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
            )
            await session.execute(
                sa.delete(cast(sa.Table, MMovieWatchedHistory.__table__)).where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
            )
            return MovieWatched()

        if (watched['position'] or 0) > 0:
            watched_at = await session.scalar(
                sa.select(MMovieWatchedHistory.watched_at)
                .where(
                    MMovieWatchedHistory.movie_id == movie_id,
                    MMovieWatchedHistory.user_id == user_id,
                )
                .order_by(MMovieWatchedHistory.watched_at.desc())
                .limit(1)
            )
            await session.execute(
                sa.update(cast(sa.Table, MMovieWatched.__table__))
                .where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
                .values(
                    position=0,
                    watched_at=watched_at,
                )
            )
        else:
            history_rows = (
                await session.execute(
                    sa.select(MMovieWatchedHistory.id, MMovieWatchedHistory.watched_at)
                    .where(
                        MMovieWatchedHistory.movie_id == movie_id,
                        MMovieWatchedHistory.user_id == user_id,
                    )
                    .order_by(MMovieWatchedHistory.watched_at.desc())
                    .limit(2)
                )
            ).all()
            await session.execute(
                sa.delete(cast(sa.Table, MMovieWatchedHistory.__table__)).where(
                    MMovieWatchedHistory.id == history_rows[0].id,
                )
            )
            await session.execute(
                sa.update(cast(sa.Table, MMovieWatched.__table__))
                .where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
                .values(
                    times=MMovieWatched.times - 1,
                    position=0,
                    watched_at=history_rows[1].watched_at,
                )
            )

        watched = (
            (
                await session.execute(
                    sa.select(MMovieWatched.__table__).where(
                        MMovieWatched.movie_id == movie_id,
                        MMovieWatched.user_id == user_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        return movie_watched_mapper(watched) if watched else MovieWatched()


async def get_movie_watched_position(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> MovieWatched | None:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(MMovieWatched.__table__).where(
                        MMovieWatched.movie_id == movie_id,
                        MMovieWatched.user_id == user_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        return movie_watched_mapper(watched) if watched else None


async def set_movie_watched_position(
    *,
    movie_id: int,
    user_id: int,
    position: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        if position == 0:
            await reset_movie_watched_position(
                user_id=user_id,
                movie_id=movie_id,
                session=session,
            )
            return
        stmt = mysql_insert(cast(sa.Table, MMovieWatched.__table__)).values(
            movie_id=movie_id,
            user_id=user_id,
            watched_at=datetime.now(tz=UTC),
            position=position,
        )
        stmt = stmt.on_duplicate_key_update(
            watched_at=stmt.inserted.watched_at,
            position=stmt.inserted.position,
        )
        await session.execute(stmt)


async def delete_movie_watched_position(
    *,
    movie_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        await reset_movie_watched_position(
            user_id=user_id, movie_id=movie_id, session=session
        )


async def reset_movie_watched_position(
    user_id: int,
    movie_id: int,
    session: AsyncSession,
) -> None:
    watched = (
        (
            await session.execute(
                sa.select(MMovieWatched.__table__).where(
                    MMovieWatched.movie_id == movie_id,
                    MMovieWatched.user_id == user_id,
                )
            )
        )
        .mappings()
        .first()
    )
    if not watched:
        return
    if (watched['times'] or 0) < 1:
        await session.execute(
            sa.delete(cast(sa.Table, MMovieWatched.__table__)).where(
                MMovieWatched.movie_id == movie_id,
                MMovieWatched.user_id == user_id,
            )
        )
        await session.execute(
            sa.delete(cast(sa.Table, MMovieWatchedHistory.__table__)).where(
                MMovieWatchedHistory.movie_id == movie_id,
                MMovieWatchedHistory.user_id == user_id,
            )
        )
        return
    if (watched['position'] or 0) > 0:
        watched_at = await session.scalar(
            sa.select(MMovieWatchedHistory.watched_at)
            .where(
                MMovieWatchedHistory.movie_id == movie_id,
                MMovieWatchedHistory.user_id == user_id,
            )
            .order_by(MMovieWatchedHistory.watched_at.desc())
            .limit(1)
        )
        await session.execute(
            sa.update(cast(sa.Table, MMovieWatched.__table__))
            .where(
                MMovieWatched.movie_id == movie_id,
                MMovieWatched.user_id == user_id,
            )
            .values(
                position=0,
                watched_at=watched_at,
            )
        )
