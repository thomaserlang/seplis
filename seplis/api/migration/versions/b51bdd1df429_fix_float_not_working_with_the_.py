"""Fix float not working with the pagination cursor

Revision ID: b51bdd1df429
Revises: 20559ab61113
Create Date: 2023-09-03 20:01:03.959896

"""

# revision identifiers, used by Alembic.
revision = 'b51bdd1df429'
down_revision = '20559ab61113'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('series', 'rating_weighted', type_=sa.DECIMAL(precision=12, scale=4), existing_type=sa.Float, existing_nullable=False, existing_server_default='0')
    op.alter_column('movies', 'rating_weighted', type_=sa.DECIMAL(precision=12, scale=4), existing_type=sa.Float, existing_nullable=False, existing_server_default='0')


def downgrade():
    pass
