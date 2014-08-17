"""user and app table

Revision ID: 5acfab2c2cd
Revises: 10859a97330e
Create Date: 2013-11-03 00:29:32.340451

"""

# revision identifiers, used by Alembic.
revision = '5acfab2c2cd'
down_revision = '10859a97330e'

from alembic import op
import sqlalchemy as sa

from seplis.api import models
from seplis.api.base.user import User
from seplis.api.base.app import App
from seplis.api import constants

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(20), unique=True),
        sa.Column('email', sa.String(100), unique=True),
        sa.Column('password', sa.String(200)),
        sa.Column('created', sa.DateTime),
        sa.Column('level', sa.Integer),
    )

    op.create_table(
        'show_followers',
        sa.Column('show_id', sa.Integer, sa.ForeignKey("shows.id", ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey("users.id", ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),
        sa.Column('datetime', sa.DateTime),
    )

    op.create_table(
        'episodes_watched',        
        sa.Column('show_id', sa.Integer, sa.ForeignKey("shows.id", ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),      
        sa.Column('user_id', sa.Integer, sa.ForeignKey("users.id", ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),  
        sa.Column('episode_number', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('times', sa.Integer, server_default='0'),
        sa.Column('position', sa.Integer),
        sa.Column('datetime', sa.DateTime),
    )

    op.create_table(
        'shows_watched',
        sa.Column('show_id', sa.Integer, sa.ForeignKey("shows.id", ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),      
        sa.Column('user_id', sa.Integer, sa.ForeignKey("users.id", ondelete='cascade', onupdate='cascade'), primary_key=True, autoincrement=False),  
        sa.Column('episode_number', sa.Integer),      
        sa.Column('position', sa.Integer),
        sa.Column('datetime', sa.DateTime),
    )

    models.base.bind = op.get_bind()
    user = User.new(
        name='root',
        email='root@root.com',
        password='$pbkdf2-sha256$12000$s9aaE0KIEaIUIiTE2Psfww$/vSRES8nTifRcem5Un4T3CYvv8aaZpOHjvF7/v9yDhc',# 123456
        level=constants.app_level_root,
    )

    op.create_table(
        'apps',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('name', sa.String(100), unique=True),
        sa.Column('client_id', sa.String(100), unique=True),
        sa.Column('client_secret', sa.String(100)),
        sa.Column('redirect_uri', sa.String(100)),  
        sa.Column('level', sa.Integer),   
        sa.Column('created', sa.DateTime),
        sa.Column('updated', sa.DateTime),   
    )

    app = App.new(
        user_id=user.id,
        name='SEPLIS',
        redirect_uri=None,
        level=constants.app_level_root,
    )

    op.create_table(
        'tokens',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('app_id', sa.Integer, sa.ForeignKey('apps.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('token', sa.String(100), primary_key=True),
        sa.Column('expires', sa.DateTime),
    )

def downgrade():
    op.drop_table('tokens')
    op.drop_table('apps')
    op.drop_table('episodes_watched')    
    op.drop_table('shows_watched')
    op.drop_table('users')
