"""rename following to watchlist and add favorite

Revision ID: 014aa789c9e2
Revises: 40c0b53bb573
Create Date: 2023-03-15 23:31:43.978588

"""

# revision identifiers, used by Alembic.
revision = '014aa789c9e2'
down_revision = '40c0b53bb573'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('series_followers', 'series_watchlist')
    op.create_table('series_favorites', 
        sa.Column('series_id',
            sa.Integer, 
            sa.ForeignKey(
                'series.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('user_id',
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('created_at', sa.DateTime),     
    )

def downgrade():
    pass
