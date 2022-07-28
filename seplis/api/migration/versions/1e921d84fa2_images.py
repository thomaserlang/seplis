"""images

Revision ID: 1e921d84fa2
Revises: 241a0df3baa
Create Date: 2014-09-24 20:27:59.191330

"""

# revision identifiers, used by Alembic.
revision = '1e921d84fa2'
down_revision = '241a0df3baa'

from alembic import op
import sqlalchemy as sa


def upgrade():    
    op.add_column('shows',
        sa.Column('index_images', sa.String(50))
    )
    op.create_table('images',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('relation_type', sa.Integer, nullable=False),
        sa.Column('relation_id', sa.Integer, nullable=False),
        sa.Column('external_name', sa.String(50)),
        sa.Column('external_id', sa.String(50)),
        sa.Column('height', sa.Integer),
        sa.Column('width', sa.Integer),
        sa.Column('hash', sa.String(64)),
        sa.Column('source_title', sa.String(200)),
        sa.Column('source_url', sa.String(200)),
        sa.Column('created', sa.DateTime),   
        sa.Column('type', sa.Integer),
    )

    op.create_index(
        'ix_relation_type_id',
        'images',
        ['relation_type', 'relation_id']
    )
    op.create_unique_constraint('uq_external_name_id', 'images', [
        'external_name',
        'external_id',
    ])


def downgrade():
    raise NotImplemented()
