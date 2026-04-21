import sqlalchemy as sa
from fastapi import Depends, Query, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get(
    '/me/watched',
    response_model=schemas.Page_cursor_result[schemas.User_watched],
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def get_user_watched(
    user: User_authenticated = Security(authenticated, scopes=['user:view_lists']),
    session: AsyncSession = Depends(get_session),
    user_can_watch: bool = Query(default=None),
):
    series_sql = sa.select(
        models.MEpisodeLastWatched.series_id.label('id'),
        sa.literal('series').label('type'),
        models.MEpisodeWatched.watched_at.label('watched_at'),
    ).where(
        models.MEpisodeLastWatched.user_id == user.id,
        models.MEpisodeWatched.user_id == models.MEpisodeLastWatched.user_id,
        models.MEpisodeWatched.series_id == models.MEpisodeLastWatched.series_id,
        models.MEpisodeWatched.episode_number
        == models.MEpisodeLastWatched.episode_number,
    )
    if user_can_watch:
        series_sql = series_sql.where(
            models.MPlayServerAccess.user_id == user.id,
            models.MPlayServerEpisode.play_server_id
            == models.MPlayServerAccess.play_server_id,
            models.MPlayServerEpisode.series_id == models.MEpisodeWatched.series_id,
            models.MPlayServerEpisode.episode_number
            == models.MEpisodeWatched.episode_number,
        )

    movies_sql = sa.select(
        models.MMovieWatched.movie_id.label('id'),
        sa.literal('movie').label('type'),
        models.MMovieWatched.watched_at.label('watched_at'),
    ).where(
        models.MMovieWatched.user_id == user.id,
        models.MMovieWatched.movie_id == models.MMovie.id,
    )
    if user_can_watch:
        movies_sql = movies_sql.where(
            models.MPlayServerAccess.user_id == user.id,
            models.MPlayServerMovie.play_server_id
            == models.MPlayServerAccess.play_server_id,
            models.MPlayServerMovie.movie_id == models.MMovieWatched.movie_id,
        )

    rows = await session.execute(
        sa.union(
            series_sql,
            movies_sql,
        )
        .order_by(sa.text('watched_at DESC, id DESC'))
        .limit(25)
    )
    rows = rows.all()

    ids = {
        'series_ids': [],
        'movie_ids': [],
    }
    for r in rows:
        if r.type == 'series':
            ids['series_ids'].append(r.id)
        elif r.type == 'movie':
            ids['movie_ids'].append(r.id)

    data = {}
    series = await session.scalars(
        sa.select(models.MSeries).where(models.MSeries.id.in_(ids['series_ids']))
    )
    for s in series:
        data[f'series-{s.id}'] = schemas.Series.model_validate(s)
    movies = await session.scalars(
        sa.select(models.MMovie).where(models.MMovie.id.in_(ids['movie_ids']))
    )
    for m in movies:
        data[f'movie-{m.id}'] = schemas.Movie.model_validate(m)

    result = []
    for r in rows:
        if r.type == 'series':
            result.append(
                schemas.User_watched(
                    type=r.type,
                    data=data[f'series-{r.id}'],
                    series=data[f'series-{r.id}'],
                )
            )
        elif r.type == 'movie':
            result.append(
                schemas.User_watched(
                    type=r.type, data=data[f'movie-{r.id}'], movie=data[f'movie-{r.id}']
                )
            )
    return schemas.Page_cursor_result(items=result)
