"""Movie extra stuff

Revision ID: f689fc38a115
Revises: 70ca870cca7a
Create Date: 2022-12-17 14:57:42.645729

"""

# revision identifiers, used by Alembic.
revision = 'f689fc38a115'
down_revision = '70ca870cca7a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('movies', sa.Column('original_title', sa.String(200)))
    op.execute('UPDATE movies SET original_title=title')
    op.add_column('movies', sa.Column('tagline', sa.String(500)))
    op.alter_column('movies', 'description', existing_type=sa.String(2000), new_column_name='plot')
    op.add_column('movies', sa.Column('budget', sa.Integer))
    op.add_column('movies', sa.Column('revenue', sa.Integer))
    op.add_column('movies', sa.Column('genres', sa.JSON(), server_default='[]', nullable=False))
    op.add_column('movies', sa.Column('popularity', sa.DECIMAL(12, 4)))
    op.add_column('movies', sa.Column('rating', sa.DECIMAL(4, 2)))
    op.create_table('movie_genres', 
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True),
        sa.Column('genre_id', sa.Integer, sa.ForeignKey('genres.id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True),
    )
    

def downgrade():
    pass
