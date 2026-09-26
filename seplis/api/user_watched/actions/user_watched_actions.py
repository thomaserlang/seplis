import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.movie.actions.movie_mapping import movie_row_mapper, select_movies
from seplis.api.movie.models.movie_model import MMovie, MMovieWatched
from seplis.api.page_cursor import PageCursor
from seplis.api.play_server.models.play_server_model import (
    MPlayServerAccess,
    MPlayServerEpisode,
    MPlayServerMovie,
)
from seplis.api.series.actions.series_mapping import select_series, series_row_mapper
from seplis.api.series.models.episode_model import MEpisodeLastWatched, MEpisodeWatched
from seplis.api.series.models.series_model import MSeries

from ..schemas.user_watched_schemas import UserWatched


async def get_user_watched(
    user_id: int,
    user_can_watch: bool | None,
    session: AsyncSession | None = None,
) -> PageCursor[UserWatched]:
    async with get_session(session) as session:
        series_sql = sa.select(
            MEpisodeLastWatched.series_id.label('id'),
            sa.literal('series').label('type'),
            MEpisodeWatched.watched_at.label('watched_at'),
        ).where(
            MEpisodeLastWatched.user_id == user_id,
            MEpisodeWatched.user_id == MEpisodeLastWatched.user_id,
            MEpisodeWatched.series_id == MEpisodeLastWatched.series_id,
            MEpisodeWatched.episode_number == MEpisodeLastWatched.episode_number,
        )
        if user_can_watch:
            series_sql = series_sql.where(
                MPlayServerAccess.user_id == user_id,
                MPlayServerEpisode.play_server_id == MPlayServerAccess.play_server_id,
                MPlayServerEpisode.series_id == MEpisodeWatched.series_id,
                MPlayServerEpisode.episode_number == MEpisodeWatched.episode_number,
            )

        movies_sql = sa.select(
            MMovieWatched.movie_id.label('id'),
            sa.literal('movie').label('type'),
            MMovieWatched.watched_at.label('watched_at'),
        ).where(
            MMovieWatched.user_id == user_id,
            MMovieWatched.movie_id == MMovie.id,
        )
        if user_can_watch:
            movies_sql = movies_sql.where(
                MPlayServerAccess.user_id == user_id,
                MPlayServerMovie.play_server_id == MPlayServerAccess.play_server_id,
                MPlayServerMovie.movie_id == MMovieWatched.movie_id,
            )

        rows = (
            (
                await session.execute(
                    sa.union(
                        series_sql,
                        movies_sql,
                    )
                    .order_by(sa.text('watched_at DESC, id DESC'))
                    .limit(25)
                )
            )
            .mappings()
            .all()
        )

        ids = {
            'series_ids': [],
            'movie_ids': [],
        }
        for row in rows:
            if row['type'] == 'series':
                ids['series_ids'].append(row['id'])
            elif row['type'] == 'movie':
                ids['movie_ids'].append(row['id'])

        series_data = {}
        series = (
            await session.execute(
                select_series().where(MSeries.id.in_(ids['series_ids']))
            )
        ).mappings()
        for item in series:
            series_data[item['id']] = series_row_mapper(item)
        movie_data = {}
        movies = (
            await session.execute(select_movies().where(MMovie.id.in_(ids['movie_ids'])))
        ).mappings()
        for item in movies:
            movie_data[item['id']] = movie_row_mapper(item)

        result = []
        for row in rows:
            if row['type'] == 'series':
                series = series_data[row['id']]
                result.append(
                    UserWatched(
                        type=row['type'],
                        data=series,
                        series=series,
                    )
                )
            elif row['type'] == 'movie':
                movie = movie_data[row['id']]
                result.append(
                    UserWatched(
                        type=row['type'],
                        data=movie,
                        movie=movie,
                    )
                )
        return PageCursor(records=result)
