"""added episode finished

Revision ID: d3609e491
Revises: 32c6ba5c064
Create Date: 2015-07-22 13:57:44.605654

"""

# revision identifiers, used by Alembic.
revision = 'd3609e491'
down_revision = '32c6ba5c064'

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.add_column('episodes_watched',
        sa.Column('completed', sa.Enum('Y', 'N'), server_default='N'),
    )
    op.drop_table('shows_watched')

def downgrade():
    raise NotImplementedError()
