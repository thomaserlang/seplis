"""added fan count to show

Revision ID: 27aaf557802
Revises: 3e6d8210fa1
Create Date: 2014-09-13 00:46:28.335427

"""

# revision identifiers, used by Alembic.
revision = '27aaf557802'
down_revision = '3e6d8210fa1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('shows',
        sa.Column('fans', sa.Integer, server_default='0')
    )
    op.add_column('users',
        sa.Column('fan_of', sa.Integer, server_default='0')
    )
    op.add_column('users',
        sa.Column('watched', sa.Integer, server_default='0')
    )

def downgrade():
    raise NotImplemented()
