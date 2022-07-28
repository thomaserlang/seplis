"""episodes

Revision ID: 31cb87f640df
Revises: 570da0d12cde
Create Date: 2013-09-28 18:00:18.914000

"""

# revision identifiers, used by Alembic.
revision = '31cb87f640df'
down_revision = '570da0d12cde'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'episodes',
        sa.Column('show_id', sa.Integer, sa.ForeignKey('shows.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False), 
        sa.Column('number', sa.Integer, primary_key=True, autoincrement=False),        
        sa.Column('title', sa.String(200)),
        sa.Column('air_date', sa.Date()),
        sa.Column('description_text', sa.Text),
        sa.Column('description_title', sa.String(45)),
        sa.Column('description_url', sa.String(200)),
        sa.Column('season', sa.Integer),
        sa.Column('episode', sa.Integer),
    )
    
def downgrade():
    op.drop_table('episodes')