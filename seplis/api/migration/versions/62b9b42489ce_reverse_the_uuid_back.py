"""Reverse the uuid back

Revision ID: 62b9b42489ce
Revises: fb4ff7dc2ba0
Create Date: 2023-08-26 08:27:18.031157

"""

# revision identifiers, used by Alembic.
revision = '62b9b42489ce'
down_revision = 'fb4ff7dc2ba0'

from alembic import op
import sqlalchemy as sa

def reverse_uuid7_mariadb(s):
    return f'{s[24:32]}-{s[32:36]}-{s[19:23]}-{s[14:18]}-{s[0:8]}{s[9:13]}'

def upgrade():
    ids = {}
    conn = op.get_bind()
    old_ids = conn.scalars(sa.text('select id from play_servers'))
    for id_ in old_ids:
        ids[id_] = reverse_uuid7_mariadb(id_)
        conn.execute(sa.text('UPDATE play_servers SET id=:new_id WHERE id=:id'), {
            'id': id_, 
            'new_id': ids[id_],
        })


def downgrade():
    pass