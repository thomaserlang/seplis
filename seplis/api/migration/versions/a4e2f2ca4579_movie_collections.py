"""Movie collections

Revision ID: a4e2f2ca4579
Revises: 97895c47bbe3
Create Date: 2023-03-10 21:01:09.939331

"""

# revision identifiers, used by Alembic.
revision = 'a4e2f2ca4579'
down_revision = '97895c47bbe3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('movie_collections',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True), 
        sa.Column('name', sa.String(200)),
    )
    op.add_column('movies', sa.Column('collection_id', 
                                      sa.Integer, 
                                      sa.ForeignKey("movie_collections.id", ondelete='cascade', onupdate='cascade'), 
                                      nullable=True, 
                                      server_default=None,
                                      ))


def downgrade():
    pass
