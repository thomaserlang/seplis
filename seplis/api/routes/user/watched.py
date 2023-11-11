import sqlalchemy as sa
from fastapi import Depends, Query, Security
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
from .router import router

@router.get('/me/watched', response_model=schemas.Page_cursor_result[schemas.User_watched],
            description='''
            **Scope required:** `user:view_lists`
            ''')
async def get_user_watched(
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_lists']),
    session: AsyncSession = Depends(get_session),
    user_can_watch: bool = Query(default=None),
):
    series_sql = sa.select(
        models.Episode_last_watched.series_id.label('id'), 
        sa.literal('series').label('type'),
        models.Episode_watched.watched_at.label('watched_at'),
    ).where(
        models.Episode_last_watched.user_id == user.id,
        models.Episode_watched.user_id == models.Episode_last_watched.user_id,
        models.Episode_watched.series_id == models.Episode_last_watched.series_id,
        models.Episode_watched.episode_number == models.Episode_last_watched.episode_number,
    )
    if user_can_watch:
        series_sql = series_sql.where(
            models.Play_server_access.user_id == user.id,
            models.Play_server_episode.play_server_id == models.Play_server_access.play_server_id,
            models.Play_server_episode.series_id == models.Episode_watched.series_id,
            models.Play_server_episode.episode_number == models.Episode_watched.episode_number,
        )

    movies_sql = sa.select(
        models.Movie_watched.movie_id.label('id'), 
        sa.literal('movie').label('type'),
        models.Movie_watched.watched_at.label('watched_at'),
    ).where(
        models.Movie_watched.user_id == user.id,
        models.Movie_watched.movie_id == models.Movie.id,
    )
    if user_can_watch:
        movies_sql = movies_sql.where(
            models.Play_server_access.user_id == user.id,
            models.Play_server_movie.play_server_id == models.Play_server_access.play_server_id,
            models.Play_server_movie.movie_id == models.Movie_watched.movie_id,
        )

    rows = await session.execute(sa.union(
        series_sql,
        movies_sql,
    ).order_by(sa.text('watched_at DESC, id DESC')).limit(25))
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
    series = await session.scalars(sa.select(models.Series).where(models.Series.id.in_(ids['series_ids'])))
    for s in series:
        data[f'series-{s.id}'] = schemas.Series.model_validate(s)
    movies = await session.scalars(sa.select(models.Movie).where(models.Movie.id.in_(ids['movie_ids'])))
    for m in movies:
        data[f'movie-{m.id}'] = schemas.Movie.model_validate(m)

    result = []
    for r in rows:
        if r.type == 'series':
            result.append(schemas.User_watched(type=r.type, data=data[f'series-{r.id}'], series=data[f'series-{r.id}']))
        elif r.type == 'movie':
            result.append(schemas.User_watched(type=r.type, data=data[f'movie-{r.id}'], movie=data[f'movie-{r.id}']))
    return schemas.Page_cursor_result(items=result)