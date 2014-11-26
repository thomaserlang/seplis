"""renamed show title field

Revision ID: 122da5c7660
Revises: 8e7907ad0b
Create Date: 2014-11-26 22:31:05.573698

"""

# revision identifiers, used by Alembic.
revision = '122da5c7660'
down_revision = '8e7907ad0b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('show_id_lookup_new', 
        sa.Column('file_show_title', sa.String(200), primary_key=True),
        sa.Column('show_title', sa.String(200)),
        sa.Column('show_id', sa.Integer),
        sa.Column('updated', sa.DateTime),
    )

    op.execute('''
        INSERT INTO 
            show_id_lookup_new (file_show_title, show_id, updated) 
        SELECT show_title, show_id, updated FROM show_id_lookup;
    ''')

    op.drop_table('show_id_lookup')
    
    op.rename_table(
        'show_id_lookup_new',
        'show_id_lookup',
    )


def downgrade():
    raise NotImplemented()
