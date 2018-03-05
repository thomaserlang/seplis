"""episode_watched_changes

Revision ID: 22d4ef0f875
Revises: 54371f572a3
Create Date: 2018-02-24 19:17:36.539818

"""

# revision identifiers, used by Alembic.
revision = '22d4ef0f875'
down_revision = '54371f572a3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


def upgrade():
    op.alter_column(
        'episodes_watched', 
        'updated_at',
        new_column_name='watched_at',
        existing_type=sa.DateTime,
    )

    op.drop_column('episodes_watched', 'completed')

    op.create_table('episode_watching',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),
        sa.Column('show_id', sa.Integer, sa.ForeignKey('shows.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False), 
        sa.Column('episode_number', sa.Integer),
    )

    con = op.get_bind()
    if con.engine.name == 'mysql':
        result = con.execute(text('''
            INSERT INTO episode_watching (show_id, episode_number, user_id)
            SELECT show_id, episode_number, user_id FROM (
                SELECT 
                    show_id, episode_number, user_id
                FROM
                    episodes_watched
                ORDER BY user_id, show_id, watched_at DESC, 
                episode_number ASC LIMIT 18446744073709551615
            ) as ew GROUP BY user_id, show_id;
        '''))

def downgrade():    
    raise NotImplemented()
