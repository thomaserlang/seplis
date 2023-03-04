import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from .. import exceptions, models


def filter_has_watched(query, filter_query: Series_query_filter):
    if filter_query.user_has_watched == None:
        return query
    if not filter_query.user:
        raise exceptions.Not_signed_in_exception()
    if filter_query.user_has_watched == True or filter_query.sort.startswith('user_last_episode_watched_at'):
        return query.where(
            models.Episode_last_watched.user_id == filter_query.user.id,
            models.Series.id == models.Episode_last_watched.series_id,
            models.Episode_watched.user_id == models.Episode_last_watched.user_id,
            models.Episode_watched.series_id == models.Episode_last_watched.series_id,
            models.Episode_watched.episode_number == models.Episode_last_watched.episode_number,
        )
    elif filter_query.user_has_watched == False:
        return query.join(
            models.Episode_last_watched,
            sa.and_(
                models.Episode_last_watched.user_id == filter_query.user.id,
                models.Series.id == models.Episode_last_watched.series_id,
            ),
            isouter=True,
        ).where(
            models.Episode_last_watched.series_id == None,
        )
    return query