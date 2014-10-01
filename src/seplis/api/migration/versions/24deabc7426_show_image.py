"""show image

Revision ID: 24deabc7426
Revises: 1e921d84fa2
Create Date: 2014-09-27 00:28:07.418123

"""

# revision identifiers, used by Alembic.
revision = '24deabc7426'
down_revision = '1e921d84fa2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('shows',
        sa.Column(
            'poster_image_id', 
            sa.Integer, 
            sa.ForeignKey(
                'images.id', 
                onupdate='cascade',
                ondelete='set null',
            )
        )
    )


def downgrade():
    raise NotImplemented()
