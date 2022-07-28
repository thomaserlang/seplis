"""remove unique from shows.title

Revision ID: 54371f572a3
Revises: 2cef22402df
Create Date: 2017-10-28 14:30:10.226274

"""

# revision identifiers, used by Alembic.
revision = '54371f572a3'
down_revision = '2cef22402df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_index('title', table_name='shows')

def downgrade():
    raise NotImplemented()
