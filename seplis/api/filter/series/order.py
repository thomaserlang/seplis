import sqlalchemy as sa

from ... import models
from .query_filter_schema import Series_query_filter


def order_query(query: any, filter_query: Series_query_filter):
    order = []
    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith('_asc') else sa.desc
        if sort.startswith('user_rating'):
            order.append(direction(sa.func.coalesce(models.MSeriesUserRating.rating, -1)))
        elif sort.startswith('user_watchlist_added_at') and filter_query.user_watchlist:
            order.append(direction(models.MSeriesWatchlist.created_at))
        elif sort.startswith('user_favorites_added_at') and filter_query.user_favorites:
            order.append(direction(models.MSeriesFavorite.created_at))
        elif (
            sort.startswith('user_last_episode_watched_at')
            and filter_query.user_has_watched
        ):
            order.append(direction(models.MEpisodeWatched.watched_at))
        elif sort.startswith('rating'):
            order.append(direction(models.MSeries.rating_weighted))
        elif sort.startswith('popularity'):
            order.append(direction(sa.func.coalesce(models.MSeries.popularity, 0)))
        elif sort.startswith('user_play_server_series_added'):
            order.append(direction(models.MPlayServerEpisode.created_at))
        elif sort.startswith('premiered'):
            order.append(
                direction(sa.func.coalesce(models.MSeries.premiered, '1970-01-01'))
            )
    return query.order_by(*order, sa.asc(models.MSeries.id))
