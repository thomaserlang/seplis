import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session

from ..models.movie_model import MMovie, MMovieWatched
from ..models.movie_watchlist_model import MMovieWatchlist
from ..schemas.movie_stats_schemas import UserMovieStats


async def get_user_movie_stats(
    user_id: int, session: AsyncSession | None = None
) -> UserMovieStats:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(
                        sa.func.count(MMovieWatched.movie_id).label('movies_watched'),
                        sa.func.sum(MMovieWatched.times).label('movie_watch_count'),
                        sa.func.sum(
                            MMovieWatched.times * sa.func.coalesce(MMovie.runtime, 0)
                        ).label('total_watch_minutes'),
                    )
                    .select_from(MMovieWatched.__table__)
                    .join(MMovie.__table__, MMovie.id == MMovieWatched.movie_id)
                    .where(MMovieWatched.user_id == user_id, MMovieWatched.times > 0)
                )
            )
            .mappings()
            .one()
        )
        watchlist = await session.scalar(
            sa.select(sa.func.count(MMovieWatchlist.movie_id)).where(
                MMovieWatchlist.user_id == user_id
            )
        )
        return UserMovieStats(
            movies_watched=int(watched['movies_watched'] or 0),
            movie_watch_count=int(watched['movie_watch_count'] or 0),
            total_watch_minutes=int(watched['total_watch_minutes'] or 0),
            movies_watchlist=int(watchlist or 0),
        )
