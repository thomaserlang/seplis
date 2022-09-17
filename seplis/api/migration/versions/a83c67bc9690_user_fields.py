"""user fields

Revision ID: a83c67bc9690
Revises: d8a21dcfd496
Create Date: 2022-09-07 20:26:27.089570

"""

# revision identifiers, used by Alembic.
revision = 'a83c67bc9690'
down_revision = 'd8a21dcfd496'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('users', 'fan_of')
    op.drop_column('users', 'watched')
    op.alter_column('users', 'name', new_column_name='username', existing_type=sa.String(45))
    op.alter_column('users', 'password', existing_type=sa.CHAR(87), type_=sa.String(200))


def downgrade():
    raise NotImplementedError()
