from datetime import date

import sqlalchemy as sa

from seplis.importer.popularity import popularity_update


def test_popularity_updates_only_changed_values_and_uses_today() -> None:
    metadata = sa.MetaData()
    titles = sa.Table(
        'titles',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('popularity', sa.Numeric(12, 4)),
    )
    history = sa.Table(
        'history',
        metadata,
        sa.Column('title_id', sa.Integer, primary_key=True),
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('popularity', sa.Numeric(12, 4)),
    )
    today = date(2026, 11, 6)
    engine = sa.create_engine('sqlite://')
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            titles.insert(),
            [
                {'id': 1, 'popularity': 2},
                {'id': 2, 'popularity': 3},
                {'id': 3, 'popularity': 4},
                {'id': 4, 'popularity': None},
                {'id': 5, 'popularity': 0},
            ],
        )
        connection.execute(
            history.insert(),
            [
                {'title_id': 1, 'date': today, 'popularity': 5},
                {'title_id': 2, 'date': today, 'popularity': 3},
                {'title_id': 3, 'date': date(2026, 11, 5), 'popularity': 9},
            ],
        )
        statement = popularity_update(titles, history, 'title_id', today)
        assert connection.execute(statement).rowcount == 3
        assert list(connection.execute(sa.select(titles).order_by(titles.c.id))) == [
            (1, 5),
            (2, 3),
            (3, 0),
            (4, 0),
            (5, 0),
        ]
        assert connection.execute(statement).rowcount == 0
