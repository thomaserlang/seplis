"""changes the image relation type to a varchar instead of int.
Updates all 1's to show.

Revision ID: 10173b4883a
Revises: 280d3ba16a8
Create Date: 2015-01-28 21:58:34.866417

"""

# revision identifiers, used by Alembic.
revision = '10173b4883a'
down_revision = '280d3ba16a8'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column(
        'images', 
        'relation_type',
        nullable=False,
        type_=sa.String(20),
    )
    op.get_bind().execute(sa.text('update images set relation_type="show";'))

def downgrade():
    pass
