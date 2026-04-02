import sqlalchemy as sa

from ... import models
from .query_filter_schema import Movie_query_filter


def order_query(query: any, filter_query: Movie_query_filter):
    order = []
    if filter_query.genre_id:
        # When filtering by genre prioritise movies with most genre hits
        order.append(sa.desc(sa.func.count(models.MMovieGenre.genre_id)))
    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith('_asc') else sa.desc
        if sort.startswith('user_watchlist_added_at') and filter_query.user_watchlist:
            order.append(direction(models.MMovieWatchlist.created_at))
        if sort.startswith('user_favorite_added_at') and filter_query.user_favorites:
            order.append(direction(models.MMovieFavorite.created_at))
        elif sort.startswith('user_last_watched_at') and filter_query.user_has_watched:
            order.append(direction(models.MMovieWatched.watched_at))
        elif sort.startswith('rating'):
            order.append(direction(models.MMovie.rating_weighted))
        elif sort.startswith('popularity'):
            order.append(direction(models.MMovie.popularity))
        elif sort.startswith('release_date'):
            order.append(direction(models.MMovie.release_date))
        elif sort.startswith('user_play_server_movie_added'):
            order.append(direction(models.MPlayServerMovie.created_at))
    return query.order_by(*order, sa.asc(models.MMovie.id))
