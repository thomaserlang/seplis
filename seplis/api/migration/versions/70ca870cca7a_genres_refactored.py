"""Genres refactored

Revision ID: 70ca870cca7a
Revises: ad52dc5692f0
Create Date: 2022-12-16 22:58:29.033052

"""

# revision identifiers, used by Alembic.
revision = '70ca870cca7a'
down_revision = 'ad52dc5692f0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('PRIMARY', 'genres', type_='primary')
    op.execute("ALTER TABLE genres ADD id INT PRIMARY KEY AUTO_INCREMENT;")
    op.alter_column('genres', 'genre', existing_type=sa.String(100), existing_nullable=False, new_column_name='name')

    op.rename_table('show_genres', 'series_genres')
    op.add_column('series_genres', sa.Column('genre_id', sa.Integer, sa.ForeignKey('genres.id', ondelete='cascade', onupdate='cascade')))
    op.alter_column('series_genres', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.drop_constraint('PRIMARY', 'series_genres', type_='primary')
    conn = op.get_bind()
    genres = conn.execute('select id, name from genres').all()
    for genre in genres:
        conn.execute(sa.text('update series_genres set genre_id=:genre_id where genre=:genre'), {
            'genre_id': genre['id'],
            'genre': genre['name'],
        })
    op.create_primary_key('pk_series_genres', 'series_genres', ['series_id', 'genre_id'])
    op.drop_column('series_genres', 'genre')
    op.create_index('ix_name', 'genres', ['name'])


def downgrade():
    pass
