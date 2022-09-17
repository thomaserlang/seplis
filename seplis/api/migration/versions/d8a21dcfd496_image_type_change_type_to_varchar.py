"""image type change type to varchar

Revision ID: d8a21dcfd496
Revises: 04b0aceac318
Create Date: 2022-09-03 22:27:37.509074

"""

# revision identifiers, used by Alembic.
revision = 'd8a21dcfd496'
down_revision = '04b0aceac318'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('images', 'type', existing_type=sa.Integer, type_=sa.String(50))
    op.execute('UPDATE images SET type="poster" WHERE type="1"')
    op.execute('UPDATE images SET relation_type="series" WHERE relation_type="show"')
    op.drop_index('ix_relation_type_id', 'images')
    op.create_index(
        'ix_relation_type_id_type',
        'images',
        ['relation_type', 'relation_id', 'type']
    )
    op.drop_column('images', 'source_title')
    op.drop_column('images', 'source_url')


def downgrade():
    raise NotImplementedError()
