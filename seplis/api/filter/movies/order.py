import sqlalchemy as sa
from ... import models
from .query_filter_schema import Movie_query_filter


def order_query(query: any, filter_query: Movie_query_filter):
    order = []
    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith('_asc') else sa.desc
        if sort.startswith('user_watchlist_added_at') and filter_query.user_watchlist != False:
            order.append(direction(models.Movie_watchlist.created_at))
        if sort.startswith('user_favorite_added_at') and filter_query.user_favorites != False:
            order.append(direction(models.Movie_favorite.created_at))
        elif sort.startswith('user_last_watched_at') and filter_query.user_has_watched != False:
            order.append(direction(models.Movie_watched.watched_at))
        elif sort.startswith('rating'):
            order.append(direction(sa.func.coalesce(models.Movie.rating, -1)))
        elif sort.startswith('popularity'):
            order.append(direction(models.Movie.popularity))
        elif sort.startswith('release_date'):
            order.append(direction(models.Movie.release_date))
        elif sort.startswith('user_play_server_movie_added'):
            order.append(direction(models.Play_server_movie.created_at))
    return query.order_by(*order, sa.asc(models.Movie.id))
