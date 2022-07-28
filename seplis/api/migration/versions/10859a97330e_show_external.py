"""show_external

Revision ID: 10859a97330e
Revises: 31cb87f640df
Create Date: 2013-09-29 13:17:59.337000

"""

# revision identifiers, used by Alembic.
revision = '10859a97330e'
down_revision = '31cb87f640df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'show_externals',
        sa.Column('show_id', sa.Integer, sa.ForeignKey('shows.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('title', sa.String(45), primary_key=True),
        sa.Column('value', sa.String(45)),
    )

    op.create_unique_constraint('uq_title_value', 'show_externals', ['title', 'value'])

def downgrade():
    op.drop_table('show_externals')