"""Image rename hash to file_id

Revision ID: 658e6daee3a1
Revises: 92b92ef5b119
Create Date: 2023-05-29 20:38:36.787330

"""

# revision identifiers, used by Alembic.
revision = '658e6daee3a1'
down_revision = '92b92ef5b119'

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.alter_column(
        'images',
        'hash',
        new_column_name='file_id',
        existing_type=sa.String(64),
    )


def downgrade() -> None:
    pass
