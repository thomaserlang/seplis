"""user created field rename

Revision ID: 6b61517732
Revises: d3609e491
Create Date: 2015-08-14 20:54:20.443300

"""

# revision identifiers, used by Alembic.
revision = '6b61517732'
down_revision = 'd3609e491'

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.alter_column(
        'users',
        'created',
        new_column_name='created_at',
        existing_type=sa.DateTime,
    )


def downgrade():
    raise NotImplementedError()
