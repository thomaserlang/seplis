"""create episodes table

Revision ID: 8e7907ad0b
Revises: None
Create Date: 2014-11-09 13:09:30.912736

"""

# revision identifiers, used by Alembic.
revision = '8e7907ad0b'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('episodes', 
        sa.Column('show_id', sa.Integer, primary_key=True),
        sa.Column('number', sa.Integer, primary_key=True),
        sa.Column('path', sa.Text),
        sa.Column('meta_data', sa.Text),
        sa.Column('modified_time', sa.DateTime),
    )

    op.create_table('episode_number_lookup', 
        sa.Column('show_id', sa.Integer, primary_key=True),
        sa.Column('lookup_type', sa.Integer, primary_key=True),
        sa.Column('lookup_value', sa.String(45), primary_key=True),        
        sa.Column('number', sa.Integer)
    )

    op.create_table('show_id_lookup_new', 
        sa.Column('file_show_title', sa.String(200), primary_key=True),
        sa.Column('show_title', sa.String(200)),
        sa.Column('show_id', sa.Integer),
        sa.Column('updated', sa.DateTime),
    )

def downgrade():
    raise NotImplemented()
