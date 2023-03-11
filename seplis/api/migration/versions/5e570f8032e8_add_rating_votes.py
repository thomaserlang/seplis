"""Add rating votes

Revision ID: 5e570f8032e8
Revises: 4159edc08eab
Create Date: 2023-03-11 22:45:59.961179

"""

# revision identifiers, used by Alembic.
revision = '5e570f8032e8'
down_revision = '4159edc08eab'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('series', sa.Column('rating_votes', sa.Integer, nullable=True))
    op.add_column('movies', sa.Column('rating_votes', sa.Integer, nullable=True))


def downgrade():
    pass
