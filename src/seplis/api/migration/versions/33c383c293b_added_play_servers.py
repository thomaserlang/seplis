"""added play servers

Revision ID: 33c383c293b
Revises: 24deabc7426
Create Date: 2014-11-02 18:36:12.656356

"""

# revision identifiers, used by Alembic.
revision = '33c383c293b'
down_revision = '24deabc7426'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'play_servers',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('updated', sa.DateTime),
        sa.Column(
            'user_id', 
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade', 
                ondelete='cascade',
            ),
        ),
        sa.Column('name', sa.String(45)),
        sa.Column('address', sa.String(200)),
        sa.Column('external_id', sa.String(36), index=True),
        sa.Column('secret', sa.String(200), index=True),
    )

    op.create_table(
        'play_access',
        sa.Column(
            'play_server_id',
            sa.Integer,
            sa.ForeignKey(
                'play_servers.id', 
                onupdate='cascade', 
                ondelete='cascade',
            ),
            primary_key=True,
        ),
        sa.Column(
            'user_id', 
            sa.Integer, 
            sa.ForeignKey(
                'users.id', 
                onupdate='cascade', 
                ondelete='cascade',
            ),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table('play_access')
    op.drop_table('play_servers')
