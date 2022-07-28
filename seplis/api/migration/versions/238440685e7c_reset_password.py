"""reset password

Revision ID: 238440685e7c
Revises: 22d4ef0f875
Create Date: 2019-03-24 16:12:40.700967

"""

# revision identifiers, used by Alembic.
revision = '238440685e7c'
down_revision = '22d4ef0f875'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'reset_password',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('key', sa.String(64), primary_key=True, unique=True),
        sa.Column('expires', sa.DateTime()),
    )


def downgrade():
    op.drop_table('reset_password')