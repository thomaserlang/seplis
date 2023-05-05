"""people

Revision ID: 92b92ef5b119
Revises: 7072ccfb43ee
Create Date: 2023-04-07 20:57:49.383506

"""

# revision identifiers, used by Alembic.
revision = '92b92ef5b119'
down_revision = '7072ccfb43ee'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'people', 
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('name', sa.String(500)),
        sa.Column('also_known_as', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('gender', sa.SMALLINT),
        sa.Column('birthday', sa.Date),
        sa.Column('deathday', sa.Date),
        sa.Column('biography', sa.String(2000)),
        sa.Column('place_of_birth', sa.String(100)),
        sa.Column('popularity', sa.DECIMAL(precision=12, scale=4)),
        sa.Column('externals', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('profile_image_id', sa.Integer, sa.ForeignKey('images.id', onupdate='cascade', ondelete='set null'))
    )

    op.create_table(
        'person_externals',
        sa.Column('person_id', sa.Integer, sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('title', sa.String(45), primary_key=True),
        sa.Column('value', sa.String(45)),
    )
    op.create_unique_constraint('uq_title_value', 'person_externals', ['title', 'value'])

    op.create_table(
        'series_cast',
        sa.Column('series_id', sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('person_id', sa.Integer, sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('character', sa.String(200)),
        sa.Column('order', sa.Integer),
        sa.Column('total_episodes', sa.Integer, nullable=False, server_default='0'),
    )
    
    op.create_table(
        'episode_cast',
        sa.Column('person_id', sa.Integer, sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('series_id', sa.Integer, sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('episode_number', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('character', sa.String(200)),
        sa.Column('order', sa.Integer),
    )

    op.create_table(
        'movie_cast',
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('person_id', sa.Integer, sa.ForeignKey('people.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('character', sa.String(100)),
        sa.Column('order', sa.Integer),
    )
    

def downgrade():
    pass
