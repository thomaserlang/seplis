import sqlalchemy as sa

from ... import exceptions, models
from .query_filter_schema import Series_query_filter


def filter_has_watched(query, filter_query: Series_query_filter):
    has_sort = (
        'user_last_episode_watched_at_asc' in filter_query.sort
        or 'user_last_episode_watched_at_desc' in filter_query.sort
    )

    if filter_query.user_has_watched is None and not has_sort:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    if filter_query.user_has_watched or has_sort:
        return query.where(
            models.Episode_last_watched.user_id == filter_query.user.id,
            models.Series.id == models.Episode_last_watched.series_id,
            models.Episode_watched.user_id == models.Episode_last_watched.user_id,
            models.Episode_watched.series_id == models.Episode_last_watched.series_id,
            models.Episode_watched.episode_number
            == models.Episode_last_watched.episode_number,
        )
    if not filter_query.user_has_watched:
        e = sa.select(1).where(
            models.Episode_last_watched.user_id == filter_query.user.id,
            models.Episode_last_watched.series_id == models.Series.id,
        )
        return query.where(sa.not_(sa.exists(e)))
    return query