"""user show ratings

Revision ID: 9af483c392ec
Revises: 52798db29b1b
Create Date: 2020-02-15 13:47:01.728018

"""

# revision identifiers, used by Alembic.
revision = '9af483c392ec'
down_revision = '52798db29b1b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('user_show_ratings',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),
        sa.Column('show_id', sa.Integer, sa.ForeignKey('shows.id', ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False), 
        sa.Column('raiting', sa.Integer),
        sa.Column('updated_at', sa.DateTime)
    )


def downgrade():
    raise NotImplemented()
