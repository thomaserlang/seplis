"""episode air date index

Revision ID: 241a0df3baa
Revises: 27aaf557802
Create Date: 2014-09-14 01:55:55.050707

"""

# revision identifiers, used by Alembic.
revision = '241a0df3baa'
down_revision = '27aaf557802'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(
        'ix_episodes_show_id_air_date',
        'episodes',
        ['show_id', 'air_date']
    )


def downgrade():
    pass
