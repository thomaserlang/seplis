"""movies

Revision ID: 04b0aceac318
Revises: 302b36a96c40
Create Date: 2022-05-23 18:40:53.642589

"""

# revision identifiers, used by Alembic.
revision = '04b0aceac318'
down_revision = '302b36a96c40'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('movies',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(200)),
        sa.Column('alternative_titles', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('externals', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('status', sa.SmallInteger),
        sa.Column('description', sa.String(2000)),
        sa.Column('language', sa.String(20)),        
        sa.Column(
            'poster_image_id', 
            sa.Integer, 
            sa.ForeignKey(
                'images.id', 
                onupdate='cascade',
                ondelete='set null',
            )
        ),
        sa.Column('runtime', sa.SmallInteger),
        sa.Column('premiered', sa.Date),
    )

    op.create_table('movie_externals', 
        sa.Column('movie_id',
            sa.Integer, 
            sa.ForeignKey(
                'movies.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('title', sa.String(45), primary_key=True),
        sa.Column('value', sa.String(45))
    )
    op.create_unique_constraint('movie_externals_uq_title_value', 'movie_externals', ['title', 'value'])

    op.create_table('movies_watched',
        sa.Column('movie_id',
            sa.Integer, 
            sa.ForeignKey(
                'movies.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('user_id',
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('times', sa.SmallInteger, server_default='0'),
        sa.Column('position', sa.SmallInteger, server_default='0'),
        sa.Column('watched_at', sa.DateTime),
    )


    op.create_table('movies_watched_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('movie_id',
            sa.Integer, 
            sa.ForeignKey(
                'movies.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=False,
            autoincrement=False,
        ),
        sa.Column('user_id',
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=False,
            autoincrement=False,
        ),
        sa.Column('watched_at', sa.DateTime),
    )
    op.create_index('ix_movies_watched_history_user_id_movie_id', 'movies_watched_history', ['user_id', 'movie_id'])


    op.create_table('movies_stared',
        sa.Column('movie_id',
            sa.Integer, 
            sa.ForeignKey(
                'movies.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('user_id',
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade',
                ondelete='cascade',
            ),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column('created_at', sa.DateTime),
    )

def downgrade():
    op.drop_table('movies')
    op.drop_table('movie_externals')
    op.drop_table('movies_watched')
