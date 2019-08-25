"""show genres

Revision ID: 52798db29b1b
Revises: 22f62dd63bd4
Create Date: 2019-08-25 15:52:19.082162

"""

# revision identifiers, used by Alembic.
revision = '52798db29b1b'
down_revision = '22f62dd63bd4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('show_genres',
        sa.Column('show_id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('genre', sa.String(100), primary_key=True),
    )
    op.create_table('genres',         
        sa.Column('genre', sa.String(100), primary_key=True),
    )

def downgrade():
    raise NotImplemented()
