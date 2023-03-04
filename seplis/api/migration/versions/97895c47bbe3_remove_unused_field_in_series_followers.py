"""Remove unused field in series_followers

Revision ID: 97895c47bbe3
Revises: 5ddba6ae2808
Create Date: 2023-03-04 17:01:27.824748

"""

# revision identifiers, used by Alembic.
revision = '97895c47bbe3'
down_revision = '5ddba6ae2808'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE series_followers DROP COLUMN IF EXISTS datetime;')
    op.execute('update series_followers set created_at="2011-01-01 00:00:00" where isnull(created_at)')


def downgrade():
    pass
