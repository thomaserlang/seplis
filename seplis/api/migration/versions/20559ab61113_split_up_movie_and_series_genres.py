"""Split up movie and series genres

Revision ID: 20559ab61113
Revises: 46047fb08936
Create Date: 2023-09-02 10:44:19.685366

"""

# revision identifiers, used by Alembic.
revision = '20559ab61113'
down_revision = '46047fb08936'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('genres', sa.Column('type', sa.String(30), nullable=True))
    op.add_column('genres', sa.Column('number_of', sa.Integer(), nullable=True, server_default='0'))
    
    op.execute(sa.text('insert into genres (name, type, number_of) select name, "movie", count(id) from movie_genres, genres where movie_genres.genre_id = genres.id group by name'))
    op.execute(sa.text('insert into genres (name, type, number_of) select name, "series", count(id) from series_genres, genres where series_genres.genre_id = genres.id group by name'))

    op.execute(sa.text('update movie_genres set genre_id = (select g2.id from genres g1, genres g2 where g1.id=genre_id and isnull(g1.type) and g2.name=g1.name and g2.type = "movie")'))
    op.execute(sa.text('update series_genres set genre_id = (select g2.id from genres g1, genres g2 where g1.id=genre_id and isnull(g1.type) and g2.name=g1.name and g2.type = "series")'))

    op.execute(sa.text('delete from genres where isnull(type)'))


def downgrade():
    pass
