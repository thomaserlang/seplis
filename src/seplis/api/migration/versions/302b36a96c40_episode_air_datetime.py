"""episode air_datetime

Revision ID: 302b36a96c40
Revises: 9af483c392ec
Create Date: 2020-02-29 20:48:52.438393

"""

# revision identifiers, used by Alembic.
revision = '302b36a96c40'
down_revision = '9af483c392ec'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('episodes',
        sa.Column('air_datetime', sa.DateTime),
    )


def downgrade():
    pass
