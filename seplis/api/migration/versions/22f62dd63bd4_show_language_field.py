"""show language field

Revision ID: 22f62dd63bd4
Revises: 1852cafc4891
Create Date: 2019-08-25 14:39:43.373197

"""

# revision identifiers, used by Alembic.
revision = '22f62dd63bd4'
down_revision = '1852cafc4891'

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.add_column('shows',
        sa.Column(
            'language', 
            sa.String(100),
        )
    )


def downgrade():
    raise NotImplementedError()
