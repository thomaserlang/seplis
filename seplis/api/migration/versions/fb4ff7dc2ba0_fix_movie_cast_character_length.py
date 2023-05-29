"""Fix movie cast character length

Revision ID: fb4ff7dc2ba0
Revises: 658e6daee3a1
Create Date: 2023-05-29 21:51:55.667377

"""

# revision identifiers, used by Alembic.
revision = 'fb4ff7dc2ba0'
down_revision = '658e6daee3a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'movie_cast',
        'character',
        existing_type=sa.String(100),
        type_=sa.String(200),
    )


def downgrade():
    pass
