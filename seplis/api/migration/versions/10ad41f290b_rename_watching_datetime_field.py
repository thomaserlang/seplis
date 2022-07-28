"""rename watching datetime field

Revision ID: 10ad41f290b
Revises: 10173b4883a
Create Date: 2015-03-24 20:48:03.334785

"""

# revision identifiers, used by Alembic.
revision = '10ad41f290b'
down_revision = '10173b4883a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'shows_watched', 
        'datetime',
        new_column_name='updated_at',
        existing_type=sa.DateTime,
    )
    op.alter_column(
        'episodes_watched', 
        'datetime',
        new_column_name='updated_at',
        existing_type=sa.DateTime,
    )


def downgrade():
    raise NotImplemented()
