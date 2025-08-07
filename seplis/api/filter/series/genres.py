import sqlalchemy as sa
from .query_filter_schema import Series_query_filter
from ... import models


def filter_genres(
    query: sa.orm.Query, filter_query: Series_query_filter
) -> sa.orm.Query:
    if filter_query.genre_id:
        # handled in order_query to prioritize series with most genre hits
        pass

    if filter_query.not_genre_id:
        genre_alias = sa.orm.aliased(models.Series_genre)
        query = query.where(
            ~sa.exists(
                sa.select(1).where(
                    genre_alias.series_id == models.Series.id,
                    genre_alias.genre_id.in_(filter_query.not_genre_id),
                )
            )
        )

    return query
