from typing import Any

import sqlalchemy as sa

from seplis.api.play_server.models.play_server_model import MPlayServerMovie

from ..models.movie_favorite_model import MMovieFavorite
from ..models.movie_model import MMovie, MMovieGenre, MMovieWatched
from ..models.movie_watchlist_model import MMovieWatchlist
from ..types.movie_filter_types import MovieQueryFilter


def order_query(query: Any, filter_query: MovieQueryFilter) -> Any:
    order = []
    if filter_query.genre_id:
        # When filtering by genre prioritise movies with most genre hits
        order.append(sa.desc(sa.func.count(MMovieGenre.genre_id)))
    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith('_asc') else sa.desc
        if sort.startswith('user_watchlist_added_at') and filter_query.user_watchlist:
            order.append(direction(MMovieWatchlist.created_at))
        if sort.startswith('user_favorite_added_at') and filter_query.user_favorites:
            order.append(direction(MMovieFavorite.created_at))
        elif sort.startswith('user_last_watched_at') and filter_query.user_has_watched:
            order.append(direction(MMovieWatched.watched_at))
        elif sort.startswith('rating'):
            order.append(direction(MMovie.rating_weighted))
        elif sort.startswith('popularity'):
            order.append(direction(MMovie.popularity))
        elif sort.startswith('release_date'):
            order.append(direction(MMovie.release_date))
        elif sort.startswith('user_play_server_movie_added'):
            order.append(direction(MPlayServerMovie.created_at))
    return query.order_by(*order, sa.asc(MMovie.id))
