"""renamed_last_episode_finished

Revision ID: 5ddba6ae2808
Revises: 9dcac2f05e5b
Create Date: 2023-03-01 22:57:01.997047

"""

# revision identifiers, used by Alembic.
revision = '5ddba6ae2808'
down_revision = '9dcac2f05e5b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('episode_last_finished', 'episode_last_watched')


def downgrade():
    pass
