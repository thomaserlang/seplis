"""Increased show and episode title length

Revision ID: 4a675e7e995
Revises: 834b7020a4
Create Date: 2017-02-25 18:50:09.550400

"""

# revision identifiers, used by Alembic.
revision = '4a675e7e995'
down_revision = '834b7020a4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'shows', 
        'title',
        type_=sa.String(300),
    )
    op.alter_column(
        'episodes', 
        'title',
        type_=sa.String(300),
    )

def downgrade():
    raise NotImplemented()
