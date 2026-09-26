from typing import Any

import sqlalchemy as sa

from seplis.api.play_server.models.play_server_model import MPlayServerEpisode

from ..models.episode_model import MEpisodeWatched
from ..models.series_favorite_model import MSeriesFavorite
from ..models.series_model import MSeries
from ..models.series_user_rating_model import MSeriesUserRating
from ..models.series_watchlist_model import MSeriesWatchlist
from ..types.series_filter_types import SeriesQueryFilter


def order_query(query: Any, filter_query: SeriesQueryFilter) -> Any:
    order = []
    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith('_asc') else sa.desc
        if sort.startswith('user_rating'):
            order.append(direction(sa.func.coalesce(MSeriesUserRating.rating, -1)))
        elif sort.startswith('user_watchlist_added_at') and filter_query.user_watchlist:
            order.append(direction(MSeriesWatchlist.created_at))
        elif sort.startswith('user_favorites_added_at') and filter_query.user_favorites:
            order.append(direction(MSeriesFavorite.created_at))
        elif (
            sort.startswith('user_last_episode_watched_at')
            and filter_query.user_has_watched
        ):
            order.append(direction(MEpisodeWatched.watched_at))
        elif sort.startswith('rating'):
            order.append(direction(MSeries.rating_weighted))
        elif sort.startswith('popularity'):
            order.append(direction(sa.func.coalesce(MSeries.popularity, 0)))
        elif sort.startswith('user_play_server_series_added'):
            order.append(direction(MPlayServerEpisode.created_at))
        elif sort.startswith('premiered'):
            order.append(direction(sa.func.coalesce(MSeries.premiered, '1970-01-01')))
    return query.order_by(*order, sa.asc(MSeries.id))
