"""renamed indices to import_from

Revision ID: 3b6b385f280
Revises: 344275444b8
Create Date: 2016-04-05 20:56:23.328867

"""

# revision identifiers, used by Alembic.
revision = '3b6b385f280'
down_revision = '344275444b8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        'shows', 
        'index_info',
        new_column_name='importer_info',
        existing_type=sa.String(50),
    )
    op.alter_column(
        'shows', 
        'index_episodes',
        new_column_name='importer_episodes',
        existing_type=sa.String(50),
    )
    op.alter_column(
        'shows', 
        'index_images',
        new_column_name='importer_images',
        existing_type=sa.String(50),
    )



def downgrade():
    raise NotImplemented()
