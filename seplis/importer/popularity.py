from datetime import date

import sqlalchemy as sa


def popularity_update(
    titles: sa.Table, history: sa.Table, title_id: str, day: date
) -> sa.Update:
    # Probe the existing (title_id, date) primary key for each title, avoiding
    # a scan of all historical dates and the intermediate reset to zero.
    current = (
        sa.select(history.c.popularity)
        .where(history.c[title_id] == titles.c.id, history.c.date == day)
        .scalar_subquery()
    )
    popularity = sa.func.coalesce(current, 0)
    return (
        sa.update(titles)
        .where(titles.c.popularity.is_distinct_from(popularity))
        .values(popularity=popularity)
    )
