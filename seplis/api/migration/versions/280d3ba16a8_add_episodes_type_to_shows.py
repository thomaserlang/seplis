"""add episodes type to shows

Revision ID: 280d3ba16a8
Revises: 33c383c293b
Create Date: 2014-11-29 20:04:11.661610

"""

# revision identifiers, used by Alembic.
revision = '280d3ba16a8'
down_revision = '33c383c293b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('shows',
        sa.Column('episode_type', sa.Integer, server_default='2'),
    )


def downgrade():
    raise NotImplemented()
