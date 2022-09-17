"""expand token

Revision ID: 9ba3d50cb498
Revises: a83c67bc9690
Create Date: 2022-09-11 20:29:15.516089

"""

# revision identifiers, used by Alembic.
revision = '9ba3d50cb498'
down_revision = 'a83c67bc9690'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('tokens', 'token',
        existing_type=sa.String(45),
        type_=sa.String(512),
    )


def downgrade():
    pass
