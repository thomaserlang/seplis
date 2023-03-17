"""History table for ratings and popularity

Revision ID: 7072ccfb43ee
Revises: 014aa789c9e2
Create Date: 2023-03-17 10:29:57.584088

"""

# revision identifiers, used by Alembic.
revision = '7072ccfb43ee'
down_revision = '014aa789c9e2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('series_rating_history', 
        sa.Column('series_id', sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('rating', sa.DECIMAL(4, 2), nullable=False),
        sa.Column('votes', sa.Integer, nullable=False),
    )

    op.create_table('movie_rating_history', 
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('rating', sa.DECIMAL(4, 2), nullable=False),
        sa.Column('votes', sa.Integer, nullable=False),
    )

    op.create_table('series_popularity_history', 
        sa.Column('series_id', sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('popularity', sa.DECIMAL(precision=12, scale=4), nullable=False),
    )

    op.create_table('movie_popularity_history', 
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True),
        sa.Column('date', sa.Date, primary_key=True),
        sa.Column('popularity', sa.DECIMAL(precision=12, scale=4), nullable=False),
    )


def downgrade():
    pass
