"""play server invites and refactor

Revision ID: ad52dc5692f0
Revises: 2252ca418e56
Create Date: 2022-12-09 22:48:05.244520

"""

# revision identifiers, used by Alembic.
revision = 'ad52dc5692f0'
down_revision = '2252ca418e56'

from alembic import op
import sqlalchemy as sa
from uuid6 import uuid7

from seplis.utils.sqlalchemy import UUID

def uuid7_mariadb():
    a = str(uuid7())
    return f'{a[24:32]}-{a[32:36]}-{a[19:23]}-{a[14:18]}-{a[0:8]}{a[9:13]}'

def upgrade():
    op.drop_constraint('play_access_ibfk_1', 'play_access', 'foreignkey')
    
    op.alter_column('play_servers', 'id', 
        existing_type=sa.Integer,
        type_=sa.String(50),
        primary_key=True
    )

    op.alter_column('play_access', 'play_server_id',
        existing_type=sa.Integer,
        type_=sa.String(50),
    )

    ids = {}
    conn = op.get_bind()
    rows = conn.execute(sa.text('select id from play_servers'))
    for r in rows.yield_per(10000):
        ids[r['id']] = uuid7_mariadb()
        conn.execute(sa.text('UPDATE play_servers SET id=:new_id WHERE id=:id'), {
            'id': r['id'], 
            'new_id': ids[r['id']],
        })
        conn.execute(sa.text('UPDATE play_access SET play_server_id=:new_id WHERE play_server_id=:id'), {
            'id': r['id'], 
            'new_id': ids[r['id']],
        })

    op.alter_column('play_servers', 'id', 
        existing_type=sa.String(50),
        type_=UUID,
        primary_key=True
    )

    op.alter_column('play_access', 'play_server_id',
        existing_type=sa.String(50),
        type_=UUID,
    )

    
    op.drop_column('play_servers', 'external_id')
    op.alter_column('play_servers', 'created', existing_type=sa.DateTime, new_column_name='created_at')
    op.alter_column('play_servers', 'updated', existing_type=sa.DateTime, new_column_name='updated_at')


    op.create_table('play_server_invites',
        sa.Column('play_server_id', UUID, sa.ForeignKey('play_servers.id', ondelete='cascade', onupdate='cascade'), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True),
        sa.Column('invite_id', UUID, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
    )


    op.rename_table('play_access', 'play_server_access')
    op.add_column('play_server_access', sa.Column('created_at', sa.DateTime))
    conn.execute(sa.text('UPDATE play_server_access SET created_at=NOW();'))


def downgrade():
    pass
