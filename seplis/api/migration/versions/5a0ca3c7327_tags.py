"""tags

Revision ID: 5a0ca3c7327
Revises: 5acfab2c2cd
Create Date: 2014-02-22 13:36:23.272327

"""

# revision identifiers, used by Alembic.
revision = '5a0ca3c7327'
down_revision = '5acfab2c2cd'

from alembic import op
from seplis.api import models
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(50)),
        sa.Column('description', sa.String(100)),
        sa.Column('type', sa.String(50)),
    )
    op.create_unique_constraint('uq_type_name', 'tags', ['type', 'name'])

    op.create_table(
        'tag_relations',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), autoincrement=False, primary_key=True),
        sa.Column('type', sa.String(50), primary_key=True),
        sa.Column('relation_id', sa.Integer, autoincrement=False, primary_key=True),
        sa.Column('tag_id', sa.Integer, sa.ForeignKey('tags.id', ondelete='cascade', onupdate='cascade'), autoincrement=False, primary_key=True),
    )

def downgrade():
    op.drop_table('tag_relations')
    op.drop_table('tags')
