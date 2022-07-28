"""Increased show and show description url length

Revision ID: 5235cd58417
Revises: 4a675e7e995
Create Date: 2017-02-25 18:56:33.397641

"""

# revision identifiers, used by Alembic.
revision = '5235cd58417'
down_revision = '4a675e7e995'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'shows', 
        'description_url',
        type_=sa.String(300),
    )
    op.alter_column(
        'episodes', 
        'description_url',
        type_=sa.String(300),
    )

def downgrade():
    raise NotImplemented()
