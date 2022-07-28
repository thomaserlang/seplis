"""Added air_time to episodes

Revision ID: 2cef22402df
Revises: 5235cd58417
Create Date: 2017-05-28 18:20:01.188628

"""

# revision identifiers, used by Alembic.
revision = '2cef22402df'
down_revision = '5235cd58417'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('episodes',
        sa.Column('air_time', sa.Time),
    )


def downgrade():
    raise NotImplemented()
