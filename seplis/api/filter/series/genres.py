import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from ... import models


def filter_genres(query, filter_query: Series_query_filter):
    if filter_query.genre_id:
        query = query.where(
            models.Series_genre.genre_id.in_(filter_query.genre_id),
            models.Series.id == models.Series_genre.series_id,
        ).group_by(models.Series.id)

    if filter_query.not_genre_id:
        genre = sa.orm.aliased(models.Series_genre)
        query = query.join(
            genre,
            sa.and_(
                genre.series_id == models.Series.id,
                genre.genre_id.in_(filter_query.not_genre_id),
            ),
            isouter=True,
        ).where(
            genre.series_id == None,
        )

    return query