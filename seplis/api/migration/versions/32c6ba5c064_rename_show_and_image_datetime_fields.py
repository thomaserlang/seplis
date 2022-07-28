"""rename show and image datetime fields

Revision ID: 32c6ba5c064
Revises: 10ad41f290b
Create Date: 2015-03-27 00:59:57.134619

"""

# revision identifiers, used by Alembic.
revision = '32c6ba5c064'
down_revision = '10ad41f290b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'shows', 
        'updated',
        new_column_name='updated_at',
        existing_type=sa.DateTime,
    )
    op.alter_column(
        'shows', 
        'created',
        new_column_name='created_at',
        existing_type=sa.DateTime,
    )
    op.alter_column(
        'images', 
        'created',
        new_column_name='created_at',
        existing_type=sa.DateTime,
    )


def downgrade():
    raise NotImplemented()