"""show and episode fields

Revision ID: 58452cdb10d
Revises: 4ea430899ae
Create Date: 2014-09-08 22:32:33.261703

"""

# revision identifiers, used by Alembic.
revision = '58452cdb10d'
down_revision = '4ea430899ae'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('shows',
        sa.Column('runtime', sa.Integer),
    )
    op.add_column('shows',
        sa.Column('genres', sa.Text),
    )
    op.add_column('shows',
        sa.Column('alternate_titles', sa.Text),
    )

    op.add_column('episodes',
        sa.Column('runtime', sa.Integer),
    )


def downgrade():
    raise NotImplemented()
