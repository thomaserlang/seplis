"""renamed show_followers to show_fans

Revision ID: 3e6d8210fa1
Revises: 58452cdb10d
Create Date: 2014-09-12 22:07:49.024193

"""

# revision identifiers, used by Alembic.
revision = '3e6d8210fa1'
down_revision = '58452cdb10d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('show_followers', 'show_fans')   

def downgrade():    
    op.rename_table('show_fans', 'show_followers')   
