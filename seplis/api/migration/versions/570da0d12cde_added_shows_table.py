"""Added shows table

Revision ID: 570da0d12cde
Revises: None
Create Date: 2013-09-23 20:15:08.823000

"""

# revision identifiers, used by Alembic.
revision = '570da0d12cde'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'shows',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('updated', sa.DateTime),
        sa.Column('status', sa.Integer, server_default='0', nullable=False),

        sa.Column('title', sa.String(200), unique=True),
        sa.Column('description_text', sa.Text),
        sa.Column('description_title', sa.String(45)),
        sa.Column('description_url', sa.String(100)),
        sa.Column('premiered', sa.Date),
        sa.Column('ended', sa.Date),
        sa.Column('externals', sa.Text),
        sa.Column('index_info', sa.String(50)),
        sa.Column('index_episodes', sa.String(50)),
        sa.Column('seasons', sa.Text),
    )

def downgrade():
    op.drop_table('shows')
