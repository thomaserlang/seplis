"""Increase revenue int size

Revision ID: 4159edc08eab
Revises: a4e2f2ca4579
Create Date: 2023-03-11 00:39:50.784483

"""

# revision identifiers, used by Alembic.
revision = '4159edc08eab'
down_revision = 'a4e2f2ca4579'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('movies', 'revenue', 
        existing_nullable=True, 
        existing_type=sa.Integer,
        type_=sa.BIGINT,
    )
    op.alter_column('movies', 'budget', 
        existing_nullable=True, 
        existing_type=sa.Integer,
        type_=sa.BIGINT,
    )


def downgrade():
    pass
