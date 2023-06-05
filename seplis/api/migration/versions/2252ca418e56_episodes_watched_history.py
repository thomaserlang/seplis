"""episode watched history

Revision ID: 2252ca418e56
Revises: 9ba3d50cb498
Create Date: 2022-10-08 14:01:46.739259

"""

# revision identifiers, used by Alembic.
revision = '2252ca418e56'
down_revision = '9ba3d50cb498'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('episodes_watched_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('series_id',
            sa.Integer, 
            sa.ForeignKey(
                'shows.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=False,
            autoincrement=False,
        ),
        sa.Column('episode_number', sa.Integer),
        sa.Column('user_id',
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=False,
            autoincrement=False,
        ),
        sa.Column('watched_at', sa.DateTime),
    )
    op.create_index('ix_episodes_watched_history_user_id_series_id_episode_number', 'episodes_watched_history', ['user_id', 'series_id', 'episode_number'])

    conn = op.get_bind()
    episodes_watched = conn.execute(sa.text('''
        SELECT show_id, user_id, episode_number, times, position, watched_at
        FROM episodes_watched 
        WHERE times>0
        ORDER BY user_id, show_id, episode_number;
    ''')).all()

    history = []
    for ew in episodes_watched:
        for i in range(ew['times']):
            history.append({
                'user_id': ew['user_id'],
                'series_id': ew['show_id'],
                'episode_number': ew['episode_number'],
                'watched_at': ew['watched_at'],
            })

    episode_watched_history = sa.sql.table('episodes_watched_history',
        sa.sql.column('series_id', sa.Integer),
        sa.sql.column('episode_number', sa.Integer),
        sa.sql.column('user_id', sa.Integer),
        sa.sql.column('watched_at', sa.DateTime),
    )
    op.bulk_insert(episode_watched_history, history)


def downgrade():
    pass
