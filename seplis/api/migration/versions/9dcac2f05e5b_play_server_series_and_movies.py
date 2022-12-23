"""Play server series and movies

Revision ID: 9dcac2f05e5b
Revises: 11d0e1d994f9
Create Date: 2022-12-22 21:35:18.878901

"""

# revision identifiers, used by Alembic.
revision = '9dcac2f05e5b'
down_revision = '11d0e1d994f9'

from alembic import op
import sqlalchemy as sa

from seplis.utils.sqlalchemy import UUID

def upgrade():
    op.create_table(
        'play_server_movies', 
        sa.Column('play_server_id', UUID, sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    op.create_table(
        'play_server_episodes', 
        sa.Column('play_server_id', UUID, sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('series_id', sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('episode_number', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

def downgrade():
    pass
