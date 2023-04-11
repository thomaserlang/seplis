from .query_filter_schema import Series_query_filter
from ... import models


def filter_genres(query, filter_query: Series_query_filter):
    if filter_query.genre_id:
        if len(filter_query.genre_id) == 1:
            query = query.where(
                models.Series_genre.genre_id == filter_query.genre_id[0],
                models.Series.id == models.Series_genre.series_id,
            )
        else:
            query = query.where(
                models.Series_genre.genre_id.in_(filter_query.genre_id),
                models.Series.id == models.Series_genre.series_id,
            ).group_by(models.Series.id)

    if filter_query.not_genre_id:
        if len(filter_query.not_genre_id) == 1:
            query = query.where(
                models.Series_genre.genre_id == filter_query.not_genre_id[0],
                models.Series.id != models.Series_genre.series_id,
            )
        else:
            query = query.where(
                models.Series_genre.genre_id.in_(filter_query.genre_id),
                models.Series.id != models.Series_genre.series_id,
            ).group_by(models.Series.id)

    return query