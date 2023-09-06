"""Fix runtime type

Revision ID: 80d7e0a4b3bf
Revises: b51bdd1df429
Create Date: 2023-09-06 21:18:18.630581

"""

# revision identifiers, used by Alembic.
revision = '80d7e0a4b3bf'
down_revision = 'b51bdd1df429'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('movies', 'runtime', type_=sa.Integer(), existing_type=sa.SmallInteger(), existing_nullable=True)


def downgrade():
    pass
