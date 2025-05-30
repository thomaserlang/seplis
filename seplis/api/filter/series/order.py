import sqlalchemy as sa

from ... import models
from .query_filter_schema import Series_query_filter


def order_query(query: any, filter_query: Series_query_filter):
    order = []

    if filter_query.genre_id:
        # When filtering by genre prioritise series with most genre hits
        genres_subquery = (
            sa.select(
                models.Series_genre.series_id,
                sa.func.count(models.Series_genre.genre_id).label("genre_count"),
            )
            .where(
                models.Series_genre.genre_id.in_(filter_query.genre_id),
            )
            .subquery()
        )
        query = query.where(
            models.Series.id == genres_subquery.c.series_id,
        )
        order.append(sa.desc(genres_subquery.c.genre_count))

    for sort in filter_query.sort:
        direction = sa.asc if sort.endswith("_asc") else sa.desc
        if sort.startswith("user_rating"):
            order.append(
                direction(sa.func.coalesce(models.Series_user_rating.rating, -1))
            )
        elif (
            sort.startswith("user_watchlist_added_at")
            and filter_query.user_watchlist != False
        ):
            order.append(direction(models.Series_watchlist.created_at))
        elif (
            sort.startswith("user_favorites_added_at")
            and filter_query.user_favorites != False
        ):
            order.append(direction(models.Series_favorite.created_at))
        elif (
            sort.startswith("user_last_episode_watched_at")
            and filter_query.user_has_watched != False
        ):
            order.append(direction(models.Episode_watched.watched_at))
        elif sort.startswith("rating"):
            order.append(direction(models.Series.rating_weighted))
        elif sort.startswith("popularity"):
            order.append(direction(models.Series.popularity))
        elif sort.startswith("user_play_server_series_added"):
            order.append(direction(models.Play_server_episode.created_at))
        elif sort.startswith("premiered"):
            order.append(
                direction(sa.func.coalesce(models.Series.premiered, "1970-01-01"))
            )
    return query.order_by(*order, sa.asc(models.Series.id))
