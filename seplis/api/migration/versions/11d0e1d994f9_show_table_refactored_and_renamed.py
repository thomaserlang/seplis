"""Show table refactored and renamed

Revision ID: 11d0e1d994f9
Revises: f689fc38a115
Create Date: 2022-12-17 17:48:27.217374

"""

# revision identifiers, used by Alembic.
revision = '11d0e1d994f9'
down_revision = 'f689fc38a115'

from alembic import op
import sqlalchemy as sa


def upgrade():
    '''
    op.rename_table('shows', 'series')
    op.rename_table('show_externals', 'series_externals')
    op.alter_column('series_externals', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.rename_table('show_fans', 'series_followers')
    op.alter_column('series_followers', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.alter_column('episodes', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.rename_table('episode_watching', 'episode_last_finished')
    op.alter_column('episode_last_finished', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.alter_column('episodes_watched', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.rename_table('user_show_ratings', 'user_series_ratings')
    op.alter_column('user_series_ratings', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.rename_table('user_show_subtitle_lang', 'user_series_settings')
    op.alter_column('user_series_settings', 'show_id', existing_type=sa.Integer, new_column_name='series_id')
    op.drop_column('series', 'fans')
    op.add_column('series', sa.Column('original_title', sa.String(200)))
    op.execute('update series set title=left(title, 200) where length(title)>200;')
    op.execute('update series set original_title=title, genres="[]"')
    op.drop_column('series', 'description_url')
    op.drop_column('series', 'description_title')
    op.execute('update series set description_text=null where length(description_text)>2000;')
    op.alter_column('series', 'description_text', 
        existing_type=sa.Text,
        type_=sa.String(2000),
        new_column_name='plot'
    )
    op.add_column('series', sa.Column('popularity', sa.DECIMAL(12, 4)))
    op.add_column('series', sa.Column('rating', sa.DECIMAL(4, 2)))
    op.add_column('series', sa.Column('tagline', sa.String(500)))
    op.drop_column('episodes', 'description_title')
    op.drop_column('episodes', 'description_url')
    op.execute('update episodes set description_text=null where length(description_text)>2000;')
    op.alter_column('episodes', 'description_text', 
        existing_type=sa.Text, 
        type_=sa.String(2000),
        new_column_name='plot',
    )
    op.add_column('episodes', sa.Column('rating', sa.DECIMAL(4, 2)))
    op.drop_column('episodes', 'air_time')    
    op.add_column('episodes', sa.Column('original_title', sa.String(200)))
    op.execute('update episodes set title=left(title, 200) where length(title)>200;')
    '''
    op.execute('update episodes set original_title=title')
    op.alter_column('episodes', 'title', 
        existing_type=sa.String(300),
        type_=sa.String(200),
    )


def downgrade():
    pass
