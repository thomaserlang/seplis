import sqlalchemy as sa
from ... import models
from .query_filter_schema import Series_query_filter


def order_query(query: any, filter_query: Series_query_filter):
    order = []
    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith('_asc') else sa.desc
        if sort.startswith('user_rating'):
            order.append(direction(sa.func.coalesce(models.Series_user_rating.rating, -1)))
        elif sort.startswith('user_followed_at') and filter_query.user_following != False:
            order.append(direction(models.Series_follower.created_at))
        elif sort.startswith('user_last_episode_watched_at') and filter_query.user_has_watched != False:
            order.append(direction(models.Episode_watched.watched_at))
        elif sort.startswith('rating'):
            order.append(direction(sa.func.coalesce(models.Series.rating, -1)))
        elif sort.startswith('popularity'):
            order.append(direction(models.Series.popularity))
        elif sort.startswith('user_play_server_series_added'):
            order.append(direction(models.Play_server_episode.created_at))
    return query.order_by(*order, sa.asc(models.Series.id))
