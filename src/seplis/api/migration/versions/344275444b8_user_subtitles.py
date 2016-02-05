"""user_subtitles

Revision ID: 344275444b8
Revises: 6b61517732
Create Date: 2016-02-05 20:01:53.126393

"""

# revision identifiers, used by Alembic.
revision = '344275444b8'
down_revision = '6b61517732'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('user_show_subtitle_lang',
        sa.Column(
            'user_id', 
            sa.Integer, 
            sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), 
            primary_key=True,
        ),
        sa.Column(
            'show_id', 
            sa.Integer, 
            sa.ForeignKey('shows.id', onupdate='cascade', ondelete='cascade'), 
            primary_key=True,
        ),
        sa.Column('subtitle_lang', sa.String(20)),
        sa.Column('audio_lang', sa.String(20)),
    )


def downgrade():
    raise NotImplemented()
