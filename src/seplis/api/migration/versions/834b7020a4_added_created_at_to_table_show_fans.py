"""Added created_at to table show_fans

Revision ID: 834b7020a4
Revises: 3b6b385f280
Create Date: 2016-08-03 13:05:11.045161

"""

# revision identifiers, used by Alembic.
revision = '834b7020a4'
down_revision = '3b6b385f280'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('show_fans', sa.Column('created_at', sa.DateTime, nullable=True))


def downgrade():
    raise NotImplemented()
