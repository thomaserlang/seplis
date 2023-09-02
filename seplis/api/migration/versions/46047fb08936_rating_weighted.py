"""Rating weighted

Revision ID: 46047fb08936
Revises: 62b9b42489ce
Create Date: 2023-09-02 09:28:55.318557

"""

# revision identifiers, used by Alembic.
revision = '46047fb08936'
down_revision = '62b9b42489ce'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('movies', sa.Column('rating_weighted', sa.Float(), nullable=False, server_default='0'))
    op.add_column('series', sa.Column('rating_weighted', sa.Float(), nullable=False, server_default='0'))

    op.execute('update movies set rating_weighted = (rating_votes / (rating_votes + 3000)) * rating + (3000 / (rating_votes + 3000)) * 6.9 where rating_votes > 0')
    op.execute('update series set rating_weighted = (rating_votes / (rating_votes + 3000)) * rating + (3000 / (rating_votes + 3000)) * 6.9 where rating_votes > 0')

    op.create_index(op.f('ix_movies_rating_weighted'), 'movies', ['rating_weighted'], unique=False)
    op.create_index(op.f('ix_series_rating_weighted'), 'series', ['rating_weighted'], unique=False)


def downgrade():
    pass
