"""rename stared to watchlist and add favorite

Revision ID: 40c0b53bb573
Revises: 5e570f8032e8
Create Date: 2023-03-15 15:41:32.744554

"""

# revision identifiers, used by Alembic.
revision = '40c0b53bb573'
down_revision = '5e570f8032e8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('movies_stared', 'movie_watchlist')
    op.create_table('movie_favorites', 
        sa.Column('movie_id',
            sa.Integer, 
            sa.ForeignKey(
                'movies.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('user_id',
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('created_at', sa.DateTime),               
    )

def downgrade():
    pass
